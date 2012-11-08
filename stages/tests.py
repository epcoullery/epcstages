from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Student, Availability, Referent

class StagesTest(TestCase):
    fixtures = ['test_fixture.json']

    def setUp(self):
        self.admin = User.objects.create_user('me', 'me@example.org', 'mepassword')
        self.client.login(username='me', password='mepassword')

    def test_export(self):
        response = self.client.get(reverse('stages_export'))
        self.assertEqual(response.status_code, 200)

    def test_new_training(self):
        student = Student.objects.get(last_name='Varrin')
        avail = Availability.objects.get(pk=2)
        response = self.client.post(reverse('new_training'),
            {'student': student.pk,
             'avail': avail.pk,
             'referent': 1})
        self.assertEqual(response.content, b'OK')
        avail = Availability.objects.get(pk=2)
        self.assertEqual(avail.training.student, student)
        
