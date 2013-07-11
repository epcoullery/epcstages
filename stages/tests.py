# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Level, Section, Period, Student, Availability, Referent
from .utils import school_year

class StagesTest(TestCase):
    fixtures = ['test_fixture.json']

    def setUp(self):
        self.admin = User.objects.create_user('me', 'me@example.org', 'mepassword')
        self.client.login(username='me', password='mepassword')

    def test_export(self):
        response1 = self.client.get(reverse('stages_export'))
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(reverse('stages_export'), {'period': '2', 'non_attr': '0'})
        self.assertEqual(response2.status_code, 200)
        self.assertGreater(len(response1.content), len(response2.content))

        response3 = self.client.get(reverse('stages_export'), {'period': '1', 'non_attr': '1'})
        self.assertEqual(response2.status_code, 200)

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


class PeriodTest(TestCase):
    def setUp(self):
        self.section = Section.objects.create(name="ASE")
        self.level1 = Level.objects.create(name='1')
        self.level2 = Level.objects.create(name='2')

    def test_period_schoolyear(self):
        per = Period.objects.create(title="Week test", section=self.section, level=self.level1,
            start_date=date(2012, 9, 12), end_date=date(2012, 9, 26))
        self.assertEqual(per.school_year, "2012 — 2013")
        per = Period.objects.create(title="Week test", section=self.section, level=self.level1,
            start_date=date(2013, 5, 2), end_date=date(2013, 7, 4))
        self.assertEqual(per.school_year, "2012 — 2013")

    def test_period_relativelevel(self):
        year = school_year(date.today(), as_tuple=True)[1]
        per = Period.objects.create(title="For next year", section=self.section, level=self.level2,
            start_date=date(year, 9, 12), end_date=date(year, 10, 1))
        self.assertEqual(per.relative_level, self.level1)

    def test_period_weeks(self):
        per = Period.objects.create(title="Week test", section=self.section, level=self.level1,
            start_date=date(2013, 9, 12), end_date=date(2013, 9, 26))
        self.assertEqual(per.weeks, 2)
