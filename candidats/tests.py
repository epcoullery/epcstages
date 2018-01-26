from datetime import date, datetime
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from stages.models import Section, Teacher
from .models import Candidate, Interview


class CandidateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            'me', 'me@example.org', 'mepassword', first_name='Hans', last_name='Schmid',
        )

    def test_interview(self):
        inter = Interview.objects.create(date=datetime(2018, 3, 10, 10, 30), room='B103')
        self.assertEqual(str(inter), 'samedi 10 mars 2018 à 10h30 : ?/? - (N) -salle:B103-???')
        ede = Section.objects.create(name='EDE')
        cand = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        t1 = Teacher.objects.create(first_name="Julie", last_name="Caux", abrev="JCA")
        t2 = Teacher.objects.create(first_name='Jeanne', last_name='Dubois')
        inter.teacher_int = t1
        inter.teacher_file = t2
        inter.candidat = cand
        inter.save()
        self.assertEqual(
            str(inter),
            'samedi 10 mars 2018 à 10h30 : Caux Julie/Dubois Jeanne - (N) -salle:B103-Dupond Henri'
        )
        self.assertEqual(cand.interview, inter)

    def test_send_confirmation_mail(self):
        ede = Section.objects.create(name='EDE')
        ase = Section.objects.create(name='ASE')
        Candidate.objects.bulk_create([
            # A mail should NOT be sent for those first 2
            Candidate(
                first_name='Jill', last_name='Simth', gender='F', section=ede,
                deposite_date=date.today(), date_confirmation_mail=date.today()),
            Candidate(first_name='Hervé', last_name='Bern', gender='M', section=ede,
                deposite_date=date.today(), canceled_file=True),
            # Good
            Candidate(first_name='Joé', last_name='Glatz', gender='F', section=ase,
                email='joe@example.org', deposite_date=date.today()),
            Candidate(first_name='Henri', last_name='Dupond', gender='M', section=ede,
                email='henri@example.org', deposite_date=date.today()),
        ])
        change_url = reverse('admin:candidats_candidate_changelist')
        self.client.login(username='me', password='mepassword')
        response = self.client.post(change_url, {
            'action': 'send_confirmation_mail',
            '_selected_action': Candidate.objects.values_list('pk', flat=True)
        }, follow=True)
        self.assertEqual(len(mail.outbox), 2)
        # Logged-in user also receives as Bcc
        self.assertEqual(mail.outbox[0].recipients(), ['henri@example.org', 'me@example.org'])
        self.assertEqual(mail.outbox[1].recipients(), ['joe@example.org', 'me@example.org'])
        # Mail content differ depending on the section
        self.assertEqual(mail.outbox[0].body, """Monsieur,

Par ce courriel, nous vous confirmons la bonne réception de votre dossier de candidature à la formation ES d’Educateur-trice de l’enfance et vous remercions de l’intérêt que vous portez à notre institution.

Celui-ci sera traité et des nouvelles vous seront communiquées par courriel durant la 2ème quinzaine du mois de février.

Dans l’intervalle, nous vous adressons, Monsieur, nos salutations les plus cordiales.


Secrétariat de l'EPC
tél. 032 886 33 00

Hans Schmid
me@example.org
""".format()
        )
        self.assertEqual(mail.outbox[1].body, """Madame, Monsieur,

Nous vous confirmons la bonne réception de l'inscription de Madame Joé Glatz dans la filière ASE pour l'année scolaire à venir.

Nous nous tenons à votre disposition pour tout renseignement complémentaire et vous prions de recevoir, Madame, Monsieur, nos salutations les plus cordiales.

Secrétariat de l'EPC
tél. 032 886 33 00

Hans Schmid
me@example.org
""".format()
        )
        # One was already set, 2 new.
        self.assertEqual(Candidate.objects.filter(date_confirmation_mail__isnull=False).count(), 3)

    def test_send_confirmation_error(self):
        ede = Section.objects.create(name='EDE')
        henri = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        change_url = reverse('admin:candidats_candidate_changelist')
        self.client.login(username='me', password='mepassword')
        with mock.patch('django.core.mail.EmailMessage.send') as mocked:
            mocked.side_effect = Exception("Error sending mail")
            response = self.client.post(change_url, {
                'action': 'send_confirmation_mail',
                '_selected_action': Candidate.objects.values_list('pk', flat=True)
            }, follow=True)
        self.assertContains(response, "Échec d’envoi pour le candidat Dupond Henri (Error sending mail)")
        henri.refresh_from_db()
        self.assertIsNone(henri.date_confirmation_mail)

    def test_convocation_ede(self):
        ede = Section.objects.create(name='EDE')
        henri = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        inter = Interview.objects.create(date=datetime(2018, 3, 10, 10, 30), room='B103', candidat=henri)
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('candidate-convocation', args=[henri.pk]))
        self.assertContains(response, '<h2>Dupond Henri</h2>')
        self.assertContains(response, '<input type="text" name="to" value="henri@example.org" size="60" id="id_to" required>', html=True)
        self.assertContains(response, """
Monsieur Henri Dupond,

Nous vous adressons par la présente votre convocation personnelle à la procédure d’admission de la filière Education de l’enfance, dipl. ES.

Vous êtes attendu-e à l’Ecole Santé-social Pierre-Coullery, rue de la Prévoyance 82, 2300 La Chaux-de-Fonds aux dates suivantes:

 - mercredi 7 mars 2018, à 13h30, salle 405, pour l’examen écrit (durée approx. 4 heures)

 - samedi 10 mars 2018 à 10h30, en salle B103, pour l’entretien d’admission (durée approx. 45 min.).

En cas d’empêchement de dernière minute, nous vous remercions d’annoncer votre absence au secrétariat (Tél. 032 886 33 00).

De plus, afin que nous puissions enregistrer définitivement votre inscription, nous vous remercions par avance
de nous faire parvenir, dans les meilleurs délais, le ou les documents suivants:
 - Formulaire d&#39;inscription, Attest. de paiement, Casier judic., CV, Texte réflexif, Photo passeport, Bilan act. prof./dernier stage, Bull. de notes

Dans l’intervalle, nous vous adressons, Monsieur, nos salutations les plus cordiales.

Secrétariat de la filière Education de l’enfance, dipl. ES
Hans Schmid
me@example.org
tél. 032 886 33 00"""
        )
        response = self.client.post(reverse('candidate-convocation', args=[henri.pk]), data={
            'id_candidate': str(henri.pk),
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

    def test_summary_pdf(self):
        ede = Section.objects.create(name='EDE')
        cand = Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        change_url = reverse('admin:candidats_candidate_changelist')
        self.client.login(username='me', password='mepassword')
        response = self.client.post(change_url, {
            'action': 'print_summary',
            '_selected_action': Candidate.objects.values_list('pk', flat=True)
        }, follow=True)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="archive_InscriptionResumes.zip"'
        )
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertGreater(len(response.content), 200)
