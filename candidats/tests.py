from datetime import date, datetime
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from stages.exports import openxml_contenttype
from stages.models import Section, Teacher
from .models import Candidate, Interview


class CandidateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            'me', 'me@example.org', 'mepassword', first_name='Hans', last_name='Schmid',
        )

    def test_total_result(self):
        ede = Section.objects.create(name='EDE')
        cand = Candidate(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        self.assertEqual(cand.total_result, 0)
        cand.examination_result = 7
        cand.interview_result = 4
        cand.file_result = 5
        self.assertEqual(cand.total_result, 16)

    def test_interview(self):
        inter = Interview.objects.create(date=datetime(2018, 3, 10, 10, 30), room='B103')
        self.assertEqual(str(inter), 'samedi 10 mars 2018 à 10h30 : ? (Ent.) / ? (Dos.) - (N) -salle:B103-???')
        ede = Section.objects.create(name='EDE')
        cand = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        t1 = Teacher.objects.create(first_name="Julie", last_name="Caux", abrev="JCA")
        t2 = Teacher.objects.create(first_name='Jeanne', last_name='Dubois', abrev="JDU")
        inter.teacher_int = t1
        inter.teacher_file = t2
        inter.candidat = cand
        inter.save()
        self.assertEqual(
            str(inter),
            'samedi 10 mars 2018 à 10h30 : JCA (Ent.) / JDU (Dos.) - (N) -salle:B103-Dupond Henri'
        )
        self.assertEqual(cand.interview, inter)

    def test_add_candidate(self):
        url = reverse('admin:candidats_candidate_add')
        post_data = dict({},
            city = 'Peseux',
            section = 'EDE',
            certificate_of_payement = 'on',
            interview = '',
            gender = 'F',
            aes_accords = '0',
            mobile = '077 999 99 99',
            registration_form = 'on',
            birth_date = '15.03.1997',
            residence_permits = '',
            corporation = '',
            _save = 'Enregistrer',
            marks_certificate = 'on',
            avs = '75609994444567',
            activity_rate = '',
            last_name = 'G.',
            deposite_date = '31.01.2018',
            police_record = 'on',
            examination_result = '',
            diploma_detail = 'Maturité linguistique',
            handicap = 'on',
            work_certificate = 'on',
            comment = 'Le casier judiciaire a été envoyé par e-mail le 30.01.2018',
            certif_of_800_general = 'on',
            instructor = '',
            validation_sfpo = '',
            email = 'caterina.g@example.org',
            file_result = '',
            cv = 'on',
            diploma_status = '2',
            pcode = '2034',
            first_name = 'Caterina',
            reflexive_text = 'on',
            diploma = '4',
            has_photo = 'on',
            certif_of_800_childhood = 'on',
            district = 'Ne',
            option = 'PS',
            interview_result = '',
            street = 'de Neuchâtel 99',
        )
        self.client.login(username='me', password='mepassword')
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

    def test_send_confirmation_mail(self):
        self.maxDiff = None

        ede = Section.objects.create(name='EDE')
        ase = Section.objects.create(name='ASE')
        Candidate.objects.bulk_create([
            # A mail should NOT be sent for those first 2
            Candidate(
                first_name='Jill', last_name='Simth', gender='F', section=ede,
                deposite_date=date.today(), confirmation_date=date.today()),
            Candidate(first_name='Hervé', last_name='Bern', gender='M', section=ede,
                deposite_date=date.today(), canceled_file=True),
            # Good
            Candidate(first_name='Henri', last_name='Dupond', gender='M', section=ede, option='ENF',
                email='henri@example.org', deposite_date=date.today()),
            Candidate(first_name='Joé', last_name='Glatz', gender='F', section=ase,
                email='joe@example.org', deposite_date=date.today()),
        ])
        self.client.login(username='me', password='mepassword')
        cand1 = Candidate.objects.get(last_name='Simth')
        response = self.client.get(reverse('candidate-confirmation', args=[cand1.pk]), follow=True)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertEqual(msg, "Une confirmation a déjà été envoyée!")

        cand2 = Candidate.objects.get(last_name='Bern')
        response = self.client.get(reverse('candidate-confirmation', args=[cand2.pk]), follow=True)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertEqual(msg, "Ce dossier a été annulé!")

        cand3 = Candidate.objects.get(last_name='Dupond')
        response = self.client.get(reverse('candidate-confirmation', args=[cand3.pk]))
        data = response.context['form'].initial
        response = self.client.post(
            reverse('candidate-confirmation', args=[cand3.pk]), data=data, follow=True
        )
        self.assertEqual(len(mail.outbox), 1)
        # Logged-in user also receives as Bcc
        self.assertEqual(mail.outbox[0].recipients(), ['henri@example.org', 'me@example.org'])
        # Mail content differ depending on the section
        self.assertEqual(mail.outbox[0].body, """Monsieur Henri Dupond,

Par ce courriel, nous vous confirmons la bonne réception de vos documents de candidature à la formation Education de l&#39;enfance, dipl. ES, option «Enfance» et vous remercions de l’intérêt que vous portez à notre institution.

Votre dossier sera traité dans les jours à venir et des nouvelles vous seront communiquées par courriel durant la 2ème quinzaine du mois de février.

Dans l’intervalle, nous vous adressons, Monsieur, nos salutations les plus cordiales.


Secrétariat de la filière Education de l’enfance, dipl. ES
Hans Schmid
me@example.org
tél. 032 886 33 00"""
        )

        mail.outbox = []
        cand4 = Candidate.objects.get(last_name='Glatz')
        response = self.client.get(reverse('candidate-confirmation', args=[cand4.pk]))
        data = response.context['form'].initial
        response = self.client.post(
            reverse('candidate-confirmation', args=[cand4.pk]), data=data, follow=True
        )
        self.assertEqual(len(mail.outbox), 1)
        # Logged-in user also receives as Bcc
        self.assertEqual(mail.outbox[0].recipients(), ['joe@example.org', 'me@example.org'])
        self.assertEqual(mail.outbox[0].body, """Madame, Monsieur,

Nous vous confirmons la bonne réception de l’inscription de Madame Joé Glatz dans la filière Assist. socio-éducatif-ve CFC pour la prochaine rentrée scolaire.

Le nom de la classe ainsi que les jours de cours vous seront communiqués dès que toutes les inscriptions seront rentrées, mais au plus tard durant la 1ère semaine de juillet.

Nous nous tenons à votre disposition pour tout renseignement complémentaire et vous prions de recevoir, Madame, Monsieur, nos salutations les plus cordiales.

Secrétariat de l’EPC
Hans Schmid
me@example.org
tél. 032 886 33 00"""
        )
        # One was already set, 2 new.
        self.assertEqual(Candidate.objects.filter(confirmation_date__isnull=False).count(), 3)

    def test_send_confirmation_error(self):
        ede = Section.objects.create(name='EDE')
        henri = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('candidate-confirmation', args=[henri.pk]))
        data = response.context['form'].initial
        with mock.patch('django.core.mail.EmailMessage.send') as mocked:
            mocked.side_effect = Exception("Error sending mail")
            response = self.client.post(
                reverse('candidate-confirmation', args=[henri.pk]), data=data, follow=True
            )
        self.assertContains(response, "Échec d’envoi pour le candidat Dupond Henri (Error sending mail)")
        henri.refresh_from_db()
        self.assertIsNone(henri.confirmation_date)

    def test_convocation_ede(self):
        henri = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section='EDE', option='ENF',
            email='henri@example.org', deposite_date=date.today()
        )
        inter = Interview.objects.create(date=datetime(2018, 3, 10, 10, 30), room='B103', candidat=henri)
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('candidate-convocation', args=[henri.pk]))
        self.assertContains(response, '<h2>Dupond Henri</h2>')
        self.assertContains(response, '<input type="text" name="to" value="henri@example.org" size="60" id="id_to" required>', html=True)
        expected_message = """Monsieur Henri Dupond,

Nous vous adressons par la présente votre convocation personnelle à la procédure d’admission de la filière Education de l’enfance, dipl. ES.

Vous êtes attendu à l’Ecole Santé-social Pierre-Coullery, rue de la Prévoyance 82, 2300 La Chaux-de-Fonds aux dates suivantes:

 - mercredi 7 mars 2018, à 13h30, salle A405, pour l’examen écrit (analyse de texte d’une durée de 2h30 env.);

 - samedi 10 mars 2018 à 10h30, en salle B103, pour l’entretien d’admission (durée 20 min.).

En cas d’empêchement de dernière minute, nous vous remercions d’annoncer votre absence au secrétariat (Tél. 032 886 33 00).

Si vous rencontrez des difficultés d’apprentissage (dyslexie, dysorthographie, etc.), nous vous rappelons que vous pouvez bénéficier d’un temps supplémentaire d’une heure au maximum pour l’examen d’admission. Si vous n’avez pas déjà joint à votre dossier de candidature un document officiel (rapport d’orthophonie par exemple), vous devez impérativement nous le faire parvenir au moins 5 jours ouvrables avant la date du premier examen.

De plus, afin que nous puissions enregistrer définitivement votre inscription, nous vous remercions par avance de nous faire parvenir, dans les meilleurs délais, le ou les documents suivants:
 - Formulaire d&#39;inscription, Attest. de paiement, Casier judic., CV, Texte réflexif, Photo passeport, Bull. de notes

Tous les documents nécessaires à compléter votre dossier se trouvent sur notre site internet à l’adresse https://www.cifom.ch/index.php/ecoles/epc/formations-epc/educateur-de-l-enfance-epc.

Sans nouvelles de votre part 5 jours ouvrables avant la date du premier examen, votre dossier ne sera pas pris en considération et vous ne pourrez pas vous présenter à l’examen d’admission.

Nous vous remercions de nous confirmer par retour de courriel que vous avez bien reçu ce message et dans l’attente du plaisir de vous rencontrer prochainement, nous vous prions d’agréer, Monsieur, nos salutations les meilleures.

Secrétariat de la filière Education de l’enfance, dipl. ES
Hans Schmid
me@example.org
tél. 032 886 33 00
"""
        self.assertEqual(response.context['form'].initial['message'], expected_message)
        # Add missing documents and resend message
        for field_name in [
                'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'reflexive_text',
                'has_photo', 'marks_certificate']:
            setattr(henri, field_name, True)
        henri.save()
        response = self.client.get(reverse('candidate-convocation', args=[henri.pk]))
        self.assertEqual(response.context['form'].initial['message'], expected_message.replace(
            """
De plus, afin que nous puissions enregistrer définitivement votre inscription, nous vous remercions par avance de nous faire parvenir, dans les meilleurs délais, le ou les documents suivants:
 - Formulaire d&#39;inscription, Attest. de paiement, Casier judic., CV, Texte réflexif, Photo passeport, Bull. de notes

Tous les documents nécessaires à compléter votre dossier se trouvent sur notre site internet à l’adresse https://www.cifom.ch/index.php/ecoles/epc/formations-epc/educateur-de-l-enfance-epc.

Sans nouvelles de votre part 5 jours ouvrables avant la date du premier examen, votre dossier ne sera pas pris en considération et vous ne pourrez pas vous présenter à l’examen d’admission.""", "")
        )

        # Now send the message
        response = self.client.post(reverse('candidate-convocation', args=[henri.pk]), data={
            'cci': 'me@example.org',
            'to': henri.email,
            'subject': "Procédure de qualification",
            'message': "Monsieur Henri Dupond, ...",
            'sender': 'me@example.org',
        })
        self.assertRedirects(response, reverse('admin:candidats_candidate_changelist'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['henri@example.org', 'me@example.org'])
        self.assertEqual(mail.outbox[0].subject, "Procédure de qualification")
        henri.refresh_from_db()
        self.assertIsNotNone(henri.convocation_date)

    def test_validation_enseignant_ede(self):
        self.maxDiff = None
        henri = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', birth_date=date(2000, 5, 15),
            street="Rue Neuve 3", pcode='2222', city='Petaouchnok',
            section='EDE', option='ENF',
            email='henri@example.org', deposite_date=date.today()
        )
        t1 = Teacher.objects.create(
            first_name="Julie", last_name="Caux", abrev="JCA", email="julie@example.org"
        )
        t2 = Teacher.objects.create(
            first_name='Jeanne', last_name='Dubois', abrev="JDU", email="jeanne@example.org"
        )
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('candidate-validation', args=[henri.pk]), follow=True)
        self.assertContains(response, "Aucun interview attribué à ce candidat pour l’instant")

        inter = Interview.objects.create(
            date=datetime(2018, 3, 10, 10, 30), room='B103', candidat=henri,
            teacher_int=t1, teacher_file=t2,
        )
        response = self.client.get(reverse('candidate-validation', args=[henri.pk]))
        expected_message = """Bonjour,

Par ce courriel, je vous informe qu'un entretien d'admission a été planifié selon les modalités suivantes:

- samedi 10 mars 2018 à 10h30, en salle B103
  Candidat :
  Monsieur Henri Dupond
  Rue Neuve 3
  2222 Petaouchnok
  Date de naiss.: 15 mai 2000

Sans nouvelle de votre part dans les 48 heures, une convocation définitive sera envoyée  au candidat.

Avec mes meilleurs messages.

Secrétariat de la filière Education de l’enfance, dipl. ES
Hans Schmid
me@example.org
tél. 032 886 33 00
"""
        self.assertEqual(response.context['form'].initial['message'], expected_message)

        data = response.context['form'].initial
        response = self.client.post(reverse('candidate-validation', args=[henri.pk]), data=data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ["julie@example.org", "jeanne@example.org", 'me@example.org'])
        self.assertEqual(mail.outbox[0].subject, "Validation de l'entretien d'admission")
        henri.refresh_from_db()
        self.assertIsNotNone(henri.validation_date)

    def test_summary_pdf(self):
        ede = Section.objects.create(name='EDE')
        cand = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        summary_url = reverse('candidate-summary', args=[cand.pk])
        self.client.login(username='me', password='mepassword')
        response = self.client.post(summary_url, follow=True)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="dupond_henri.pdf"'
        )
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertGreater(len(response.content), 200)

    def test_export_candidates(self):
        ede = Section.objects.create(name='EDE')
        Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        Candidate.objects.create(
            first_name='Joé', last_name='Glatz', gender='F', section=ede,
            email='joe@example.org', deposite_date=date.today()
        )

        change_url = reverse('admin:candidats_candidate_changelist')
        self.client.login(username='me', password='mepassword')
        response = self.client.post(change_url, {
            'action': 'export_candidates',
            '_selected_action': Candidate.objects.values_list('pk', flat=True)
        }, follow=True)
        self.assertEqual(response['Content-Type'], openxml_contenttype)
