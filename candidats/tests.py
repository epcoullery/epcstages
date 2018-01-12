from datetime import date
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from stages.models import Section
from .models import Candidate


class CandidateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            'me', 'me@example.org', 'mepassword', first_name='Hans', last_name='Schmid',
        )

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
        self.assertEqual(mail.outbox[0].recipients(), ['henri@example.org'])
        self.assertEqual(mail.outbox[1].recipients(), ['joe@example.org'])
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
        Candidate.objects.create(
            first_name='Henri', last_name='Dupond', gender='M', section=ede,
            email='henri@example.org', deposite_date=date.today()
        )
        change_url = reverse('admin:candidats_candidate_changelist')
        self.client.login(username='me', password='mepassword')
        with mock.patch('candidats.admin.send_mail') as mocked:
            mocked.side_effect = Exception("Error sending mail")
            response = self.client.post(change_url, {
                'action': 'send_confirmation_mail',
                '_selected_action': Candidate.objects.values_list('pk', flat=True)
            }, follow=True)
        self.assertContains(response, "Échec d’envoi pour le candidat Dupond Henri (Error sending mail)")
