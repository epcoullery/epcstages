import json
import os
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.html import escape

from .models import (
    Level, Domain, Section, Klass, Period, Student, Corporation, Availability,
    CorpContact, Teacher, Training, Course,
)
from .utils import school_year


class StagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Section.objects.bulk_create([
            Section(name='ASE'), Section(name='ASSC'), Section(name='EDE'), Section(name='EDS')
        ])
        sect_ase = Section.objects.get(name='ASE')
        lev1 = Level.objects.create(name='1')
        lev2 = Level.objects.create(name='2')
        klass1 = Klass.objects.create(name="1ASE3", section=sect_ase, level=lev1)
        klass2 = Klass.objects.create(name="2ASE3", section=sect_ase, level=lev2)
        klass3 = Klass.objects.create(name="2EDS", section=Section.objects.get(name='EDS'), level=lev2)
        dom_hand = Domain.objects.create(name="handicap")
        dom_pe = Domain.objects.create(name="petite enfance")
        corp = Corporation.objects.create(
            name="Centre pédagogique XY", typ="Institution", street="Rue des champs 12",
            city="Moulineaux", pcode="2500",
        )
        contact = CorpContact.objects.create(
            corporation=corp, title="Monsieur", first_name="Jean", last_name="Horner",
            is_main=True, role="Responsable formation",
        )
        Student.objects.bulk_create([
            Student(first_name="Albin", last_name="Dupond", birth_date="1994-05-12",
                    pcode="2300", city="La Chaux-de-Fonds", klass=klass1),
            Student(first_name="Justine", last_name="Varrin", birth_date="1994-07-12",
                    pcode="2000", city="Neuchâtel", klass=klass1),
            Student(first_name="Elvire", last_name="Hickx", birth_date="1994-05-20",
                    pcode="2053", city="Cernier", klass=klass1),
            Student(first_name="André", last_name="Allemand", birth_date="1994-10-11",
                    pcode="2314", city="La Sagne", klass=klass2),
            Student(first_name="Gil", last_name="Schmid", birth_date="1996-02-14",
                    pcode="2000", city="Neuchâtel", klass=klass3, corporation=corp),
        ])
        ref1 = Teacher.objects.create(first_name="Julie", last_name="Caux", abrev="JCA")
        cls.p1 = Period.objects.create(
            title="Stage de pré-sensibilisation", start_date="2012-11-26", end_date="2012-12-07",
            section=sect_ase, level=lev1,
        )
        p2 = Period.objects.create(
            title="Stage final", start_date="2013-02-01", end_date="2013-03-15",
            section=sect_ase, level=lev2,
        )
        av1 = Availability.objects.create(
            corporation=corp, domain=dom_hand, period=cls.p1, contact=contact,
            comment="Dispo pour pré-sensibilisation",
        )
        Availability.objects.create(
            corporation=corp, domain=dom_pe, period=cls.p1, contact=contact,
            comment="Dispo prioritaire", priority=True,
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

    def test_attribution_view(self):
        response = self.client.get(reverse('attribution'))
        # Section select
        self.assertContains(response,
            '<option value="%d">ASE</option>' % Section.objects.get(name='ASE').pk)
        # Referent select
        self.assertContains(response,
            '<option value="%d">Caux Julie (0)</option>' % Teacher.objects.get(abrev="JCA").pk)

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

    def test_period_availabilities(self):
        # Testing here because PeriodTest does not have all data at hand.
        response = self.client.get(reverse('period_availabilities', args=[self.p1.pk]))
        decoded = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(decoded), 2)
        self.assertEqual([item['priority'] for item in decoded], [True, False])

    def test_export_update_forms(self):
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('print_update_form'))
        self.assertEqual(
            response['Content-Disposition'], 'attachment; filename="modification.zip"'
        )
        self.assertGreater(int(response['Content-Length']), 10)


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


class TeacherTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser('me', 'me@example.org', 'mepassword')
        cls.teacher = Teacher.objects.create(
            first_name='Jeanne', last_name='Dubois', birth_date='1974-08-08'
        )
        Course.objects.create(
            teacher=cls.teacher, period=8, subject='#ASE Colloque', imputation='ASSCFE',
        )
        Course.objects.create(
            teacher=cls.teacher, period=4, subject='Sém. enfance 2', imputation='EDEpe',
        )

    def test_export_charge_sheet(self):
        change_url = reverse('admin:stages_teacher_changelist')
        self.client.login(username='me', password='mepassword')
        response = self.client.post(change_url, {
            'action': 'print_charge_sheet',
            '_selected_action': Teacher.objects.values_list('pk', flat=True)
        }, follow=True)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="archive_FeuillesDeCharges.zip"'
        )
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertGreater(len(response.content), 200)

    def test_calc_activity(self):
        expected = {
            'tot_mandats': 8,
            'tot_ens': 4,
            'tot_formation': 2,
            'tot_trav': 14,
            'tot_paye': 14,
            'report': 0,
        }
        effective = self.teacher.calc_activity()
        self.assertEqual(list(effective['mandats']), list(Course.objects.filter(subject__startswith='#')))
        del effective['mandats']
        self.assertEqual(effective, expected)
        # Second time for equivalence test
        effective = self.teacher.calc_activity()
        del effective['mandats']
        self.assertEqual(effective, expected)

    def test_calc_imputations(self):
        result = self.teacher.calc_imputations()
        self.assertEqual(result[1]['ASSC'], 9)
        self.assertEqual(result[1]['EDEpe'], 5)
        # Test with only EDE data
        t2 = Teacher.objects.create(
            first_name='Isidore', last_name='Gluck', birth_date='1986-01-01'
        )
        Course.objects.create(
            teacher=t2, period=4, subject='Cours EDE', imputation='EDE',
        )
        result = t2.calc_imputations()
        self.assertEqual(result[1]['EDEpe'], 0)
        self.assertEqual(result[1]['EDEps'], 4)

    def test_export_imputations(self):
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('imputations_export'))
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename=Imputations_export%s.xlsx' % date.strftime(date.today(), '%Y-%m-%d')
        )


class ImportTests(TestCase):
    def setUp(self):
        User.objects.create_user('me', 'me@example.org', 'mepassword')

    def test_import_gan(self):
        path = os.path.join(os.path.dirname(__file__), 'test_files', 'EXPORT_GAN.xlsx')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-students'), {'upload': fh}, follow=True)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertIn("La classe '1ASEFEa' n'existe pas encore", msg)

        lev1 = Level.objects.create(name='1')
        Klass.objects.create(
            name='1ASEFEa',
            section=Section.objects.create(name='ASE'),
            level=lev1,
        )
        Klass.objects.create(
            name='1EDS',
            section=Section.objects.create(name='EDE'),
            level=lev1,
        )
        with open(path, 'rb') as fh:  # , override_settings(DEBUG=True):
            response = self.client.post(reverse('import-students'), {'upload': fh}, follow=True)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertIn("Created objects: 2", msg)

    def test_import_hp(self):
        teacher = Teacher.objects.create(
            first_name='Jeanne', last_name='Dupond', birth_date='1974-08-08'
        )
        path = os.path.join(os.path.dirname(__file__), 'test_files', 'HYPERPLANNING.txt')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-hp'), {'upload': fh}, follow=True)
        self.assertContains(response, "Created objects: 13, modified objects: 10")
        self.assertEqual(teacher.course_set.count(), 13)
