from datetime import date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import (
    Level, Domain, Section, Klass, Period, Student, Corporation, Availability,
    CorpContact, Referent, Training
)
from .utils import school_year


class StagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Section.objects.bulk_create([
            Section(name='ASE'), Section(name='ASSC'), Section(name='EDE')
        ])
        sect_ase = Section.objects.get(name='ASE')
        lev1 = Level.objects.create(name='1')
        lev2 = Level.objects.create(name='2')
        klass1 = Klass.objects.create(name="1ASE3", section=sect_ase, level=lev1)
        klass2 = Klass.objects.create(name="2ASE3", section=sect_ase, level=lev2)
        dom_hand = Domain.objects.create(name="handicap")
        dom_pe = Domain.objects.create(name="petite enfance")
        Student.objects.bulk_create([
            Student(first_name="Albin", last_name="Dupond", birth_date="1994-05-12",
                    pcode="2300", city="La Chaux-de-Fonds", klass=klass1),
            Student(first_name="Justine", last_name="Varrin", birth_date="1994-07-12",
                    pcode="2000", city="Neuchâtel", klass=klass1),
            Student(first_name="Elvire", last_name="Hickx", birth_date="1994-05-20",
                    pcode="2053", city="Cernier", klass=klass1),
            Student(first_name="André", last_name="Allemand", birth_date="1994-10-11",
                    pcode="2314", city="La Sagne", klass=klass2),
        ])
        ref1 = Referent.objects.create(first_name="Julie", last_name="Caux", abrev="JCA")
        corp = Corporation.objects.create(
            name="Centre pédagogique XY", typ="Institution", street="Rue des champs 12",
            city="Moulineaux", pcode="2500",
        )
        contact = CorpContact.objects.create(
            corporation=corp, title="Monsieur", first_name="Jean", last_name="Horner",
            is_main=True, role="Responsable formation",
        )
        p1 = Period.objects.create(
            title="Stage de pré-sensibilisation", start_date="2012-11-26", end_date="2012-12-07",
            section=sect_ase, level=lev1,
        )
        p2 = Period.objects.create(
            title="Stage final", start_date="2013-02-01", end_date="2013-03-15",
            section=sect_ase, level=lev2,
        )
        av1 = Availability.objects.create(
            corporation=corp, domain=dom_hand, period=p1, contact=contact,
            comment="Dispo pour pré-sensibilisation",
        )
        Availability.objects.create(
            corporation=corp, domain=dom_pe, period=p1, contact=contact,
            comment="",
        )
        av3 = Availability.objects.create(
            corporation=corp, domain=dom_pe, period=p2,
            comment="Dispo pour stage final",
        )
        Training.objects.create(
            availability=av1, student=Student.objects.get(first_name="Albin"), referent=ref1,
        )
        Training.objects.create(
            availability=av3, student=Student.objects.get(first_name="André"), referent=ref1,
        )
        cls.admin = User.objects.create_user('me', 'me@example.org', 'mepassword')

    def setUp(self):
        self.client.login(username='me', password='mepassword')

    def test_export(self):
        response1 = self.client.get(reverse('stages_export', args=['all']))
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

    def test_archived_trainings(self):
        """
        Once a student is archived, training data are serialized in its archive_text field.
        """
        st = Student.objects.get(first_name="Albin")
        st.archived = True
        st.save()
        self.assertGreater(len(st.archived_text), 0)
        arch = eval(st.archived_text)
        self.assertEqual(arch[0]['corporation'], "Centre pédagogique XY, 2500 Moulineaux")
        # Un-archiving should delete archived_text content
        st.archived = False
        st.save()
        self.assertEqual(st.archived_text, "")


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
