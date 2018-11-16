import json
import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.html import escape

from candidats.models import Candidate
from .models import (
    Level, Domain, Section, Klass, Option, Period, Student, Corporation, Availability,
    CorpContact, Teacher, Training, Course,
)
from .utils import school_year


class StagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Section.objects.bulk_create([
            Section(name='MP_ASE'), Section(name='MP_ASSC'), Section(name='EDE'), Section(name='EDS')
        ])
        sect_ase = Section.objects.get(name='MP_ASE')
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
            corporation=corp, civility="Monsieur", first_name="Jean", last_name="Horner",
            is_main=True, role="Responsable formation",
        )
        Student.objects.bulk_create([
            Student(first_name="Albin", last_name="Dupond", birth_date="1994-05-12",
                    pcode="2300", city="La Chaux-de-Fonds", email="albin@example.org",
                    klass=klass1),
            Student(first_name="Justine", last_name="Varrin", birth_date="1994-07-12",
                    pcode="2000", city="Neuchâtel", klass=klass1),
            Student(first_name="Elvire", last_name="Hickx", birth_date="1994-05-20",
                    pcode="2053", city="Cernier", klass=klass1),
            Student(first_name="André", last_name="Allemand", birth_date="1994-10-11",
                    pcode="2314", city="La Sagne", klass=klass2),
            Student(first_name="Gil", last_name="Schmid", birth_date="1996-02-14",
                    pcode="2000", city="Neuchâtel", klass=klass3, corporation=corp),
        ])
        ref1 = Teacher.objects.create(
            first_name="Julie", last_name="Caux", abrev="JCA", email="julie@eample.org",
            civility="Madame",
        )
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
        cls.admin = User.objects.create_superuser(
            'me', 'me@example.org', 'mepassword', first_name='Jean', last_name='Valjean',
        )

    def setUp(self):
        self.client.login(username='me', password='mepassword')

    def test_export_stages(self):
        response1 = self.client.get(reverse('stages_export', args=['all']))
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(reverse('stages_export'), {'period': '2', 'non_attr': '0'})
        self.assertEqual(response2.status_code, 200)
        self.assertGreater(len(response1.content), len(response2.content))

        response3 = self.client.get(reverse('stages_export'), {'period': '1', 'non_attr': '1'})
        self.assertEqual(response2.status_code, 200)

    def test_export_students(self):
        response = self.client.get(reverse('general-export'))
        self.assertEqual(response.status_code, 200)

    def test_export_qualif_ede(self):
        response = self.client.get(reverse('export-qualif-ede'))
        self.assertEqual(response.status_code, 200)

    def test_export_sap(self):
        response = self.client.get(reverse('export_sap'))
        self.assertEqual(response.status_code, 200)

    def test_student_change_view(self):
        klass_ede = Klass.objects.create(
            name="2EDEps",
            section=Section.objects.get(name='EDE'),
            level=Level.objects.get(name='2')
        )
        student_ede = Student.objects.create(
            first_name="Claire", last_name="Fontaine", birth_date="2000-01-02",
            pcode="2000", city="Neuchâtel", klass=klass_ede
        )
        response = self.client.get(
            reverse("admin:stages_student_change", args=(student_ede.pk,))
        )
        self.assertContains(response, "Factures de supervision")
        student_non_ede = Student.objects.exclude(klass__section__name='EDE').first()
        response = self.client.get(
            reverse("admin:stages_student_change", args=(student_non_ede.pk,))
        )
        self.assertNotContains(response, "Factures de supervision")

    def test_attribution_view(self):
        response = self.client.get(reverse('attribution'))
        # Section select
        self.assertContains(response,
            '<option value="%d">MP_ASE</option>' % Section.objects.get(name='MP_ASE').pk)
        # Referent select
        self.assertContains(response,
            '<option value="%d">Caux Julie (0)</option>' % Teacher.objects.get(abrev="JCA").pk)

    def test_new_training(self):
        student = Student.objects.get(last_name='Varrin')
        avail = Availability.objects.filter(priority=True).first()
        response = self.client.post(reverse('new_training'),
            {'student': student.pk,
             'avail': avail.pk,
             'referent': Teacher.objects.first().pk})
        self.assertEqual(response.content, b'OK')
        avail.refresh_from_db()
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
        response = self.client.get(reverse('print_update_form') + '?date=14.09.2018')
        self.assertEqual(
            response['Content-Disposition'], 'attachment; filename="modification.zip"'
        )
        self.assertGreater(int(response['Content-Length']), 10)

    def test_send_ede_convocation(self):
        st = Student.objects.get(first_name="Albin")
        self.client.login(username='me', password='mepassword')
        url = reverse('student-ede-convocation', args=[st.pk])
        response = self.client.get(url, follow=True)
        for err in ("La date d’examen est manquante",
                    "La salle d’examen n’est pas définie",
                    "L’expert externe n’est pas défini",
                    "L’expert interne n’est pas défini"):
            self.assertContains(response, err)
        st.date_exam = datetime(2018, 6, 28, 12, 00)
        st.room = "B123"
        st.expert = CorpContact.objects.get(last_name="Horner")
        st.internal_expert = Teacher.objects.get(last_name="Caux")
        st.save()
        response = self.client.get(url, follow=True)
        self.assertContains(response, "L’expert externe n’a pas de courriel valide !")
        st.expert.email = "horner@example.org"
        st.expert.save()
        response = self.client.get(url)
        expected_message = """ Albin Dupond,
Madame Julie Caux,
Monsieur Jean Horner,


Nous vous informons que la soutenance du travail de diplôme de  Albin Dupond aura lieu dans les locaux de l’Ecole Santé-social Pierre-Coullery, rue de la Prévoyance 82, 2300 La Chaux-de-Fonds en date du:

 - jeudi 28 juin 2018 à 12h00 en salle B123


Nous informons également Monsieur Horner que le mémoire lui est adressé ce jour par courrier postal.


Nous vous remercions de nous confirmer par retour de courriel que vous avez bien reçu ce message et dans l’attente du plaisir de vous rencontrer prochainement, nous vous prions d’agréer, Madame, Messieurs, nos salutations les meilleures.



Secrétariat de la filière Education de l’enfance, dipl. ES
Jean Valjean
me@example.org
tél. 032 886 33 00
"""
        self.assertEqual(response.context['form'].initial['message'], expected_message)
        # Now send the message
        response = self.client.post(url, data={
            'cci': 'me@example.org',
            'to': st.email,
            'subject': "Convocation",
            'message': "Monsieur Albin, ...",
            'sender': 'me@example.org',
        })
        self.assertEqual(len(mail.outbox), 1)
        st.refresh_from_db()
        self.assertIsNotNone(st.date_soutenance_mailed)

    def test_print_ede_compensation_forms(self):
        st = Student.objects.get(first_name="Albin")
        url = reverse('print-expert-compens-ede', args=[st.pk])
        self.client.login(username='me', password='mepassword')
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Toutes les informations ne sont pas disponibles")

        st.expert = CorpContact.objects.get(last_name="Horner")
        st.internal_expert = Teacher.objects.get(last_name="Caux")
        st.date_exam = datetime(2018, 6, 28, 12, 00)
        st.room = "B123"
        st.save()
        self.client.login(username='me', password='mepassword')
        response = self.client.post(url, follow=True)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="dupond_albin_Expert.pdf"'
        )
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertGreater(len(response.content), 200)
        # Expert without corporation
        st.expert = CorpContact.objects.create(first_name='James', last_name='Bond')
        st.save()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Mentor form
        st.mentor = CorpContact.objects.get(last_name="Horner")
        st.save()
        response = self.client.post(reverse('print-mentor-compens-ede', args=[st.pk]), follow=True)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="dupond_albin_Indemn_mentor.pdf"'
        )
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertGreater(len(response.content), 200)

    def test_EDEpe_klass(self):
        lev3 = Level.objects.create(name='3')
        klass4 = Klass.objects.create(name="3EDEp_pe", section=Section.objects.get(name='EDE'), level=lev3)
        self.assertTrue(klass4.is_Ede_pe())
        klass5 = Klass.objects.create(name="3EDEpe", section=Section.objects.get(name='EDE'), level=lev3)
        self.assertTrue(klass5.is_Ede_pe())

    def test_EDEps_klass(self):
        lev3 = Level.objects.create(name='3')
        klass4 = Klass.objects.create(name="3EDEp_ps", section=Section.objects.get(name='EDE'), level=lev3)
        self.assertTrue(klass4.is_Ede_ps())
        klass5 = Klass.objects.create(name="3EDEps", section=Section.objects.get(name='EDE'), level=lev3)
        self.assertTrue(klass5.is_Ede_ps())


class PeriodTest(TestCase):
    def setUp(self):
        self.section = Section.objects.create(name="MP_ASE")
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
            first_name='Jeanne', last_name='Dubois', birth_date='1974-08-08',
            rate=50.0, next_report=1,
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
        self.assertEqual(self.teacher.next_report, 0)

        # Test over max hours per year for a full time
        self.teacher.rate = 100.0
        self.teacher.save()
        crs = Course.objects.create(
            teacher=self.teacher, period=settings.MAX_ENS_PERIODS - 4, subject='Cours principal', imputation='ASSCFE',
        )
        effective = self.teacher.calc_activity()
        del effective['mandats']
        self.assertEqual(effective, {
            'tot_mandats': 8,
            'tot_ens': settings.MAX_ENS_PERIODS,
            'tot_formation': settings.MAX_ENS_FORMATION + 1,
            'tot_trav': settings.MAX_ENS_PERIODS + settings.MAX_ENS_FORMATION + 1 + 8,
            'tot_paye': settings.MAX_ENS_PERIODS + settings.MAX_ENS_FORMATION,
            'report': 8 + 1,
        })
        self.assertEqual(self.teacher.next_report, 8 + 1)

        # Test below max hours per year for a full time
        crs.period = settings.MAX_ENS_PERIODS - 4 - 10
        crs.save()
        effective = self.teacher.calc_activity()
        del effective['mandats']
        self.assertEqual(effective, {
            'tot_mandats': 8,
            'tot_ens': settings.MAX_ENS_PERIODS - 10,
            'tot_formation': settings.MAX_ENS_FORMATION,
            'tot_trav': settings.MAX_ENS_PERIODS + settings.MAX_ENS_FORMATION + 8 - 10,
            'tot_paye': settings.MAX_ENS_PERIODS + settings.MAX_ENS_FORMATION,
            'report': -2,
        })
        self.assertEqual(self.teacher.next_report, -2)

    def test_calc_imputations(self):
        ratio = {'edepe': 0.45, 'asefe': 0.45, 'asscfe': 0.55}
        result = self.teacher.calc_imputations(ratio)
        self.assertEqual(result[1]['ASSCFE'], 9)
        self.assertEqual(result[1]['EDEpe'], 5)

        # Test with only ASSC data
        t2 = Teacher.objects.create(
            first_name='Isidore', last_name='Gluck', birth_date='1986-01-01'
        )
        Course.objects.create(
            teacher=t2, period=24, subject='#ASSCE Colloque', imputation='ASSC',
        )
        Course.objects.create(
            teacher=t2, period=130, subject='#Coaching', imputation='ASSC',
        )
        Course.objects.create(
            teacher=t2, period=275, subject='Cours MP ASSC', imputation='MPS',
        )
        Course.objects.create(
            teacher=t2, period=450, subject='Cours ASSCFE', imputation='ASSCFE',
        )

        t2.previous_report = 10

        ratio = {'edepe': 0.45, 'asefe': 0.45, 'asscfe': 0.55}

        result = t2.calc_imputations(ratio)

        self.assertEqual(result[0]['tot_paye'], 1005)
        self.assertEqual(result[0]['tot_formation'], 116)
        self.assertEqual(result[0]['tot_mandats'], 154)
        self.assertEqual(result[1]['ASSCFE'], 606)
        self.assertEqual(result[1]['MPS'], 389)



    def test_export_imputations(self):
        self.client.login(username='me', password='mepassword')
        response = self.client.get(reverse('imputations_export'))
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename=Imputations_export_%s.xlsx' % date.strftime(date.today(), '%Y-%m-%d')
        )


class ImportTests(TestCase):
    def setUp(self):
        User.objects.create_user('me', 'me@example.org', 'mepassword')

    def tearDown(self):
        # Clean uploaded bulletins
        bulletins_dir = os.path.join(settings.MEDIA_ROOT, 'bulletins')
        for f in os.listdir(bulletins_dir):
            os.remove(os.path.join(bulletins_dir, f))

    def check_form_errors(self, response):
        if ('form' in response.context and response.context['form'].is_bound
                and not response.context['form'].is_valid()):
            self.fail(response.context['form'].errors)

    def test_import_students_EPC(self):
        """
        Import CLOEE file for FE students (ASAFE, ASEFE, ASSCF, EDE, EDS) version 2018!!

        Student :
        - S. Lampion, 1ASSCFEa
        - T. Tournesol, 1EDS18-20

        Candidate:
        - B. Castafiore, 2EDEpe

        Export CLOEE:
        - S. Lampion, 2ASSFEa
        - B. Castafiore, 2EDEpe
        - A. Haddock, 2EDS18-20

        Results in Student:
        - S. Lampion, 2ASSFEa (Student data + Cloee klass)
        - B. Castafiore, 2EDEpe (Candidate data + Cloee klass)
        - A. Haddock, 2EDS18-20 (Cloee data) + Warning!
        - T. Tournesol, archived
        """
        lev1 = Level.objects.create(name='1')
        lev2 = Level.objects.create(name='2')
        assc = Section.objects.create(name='ASSC')
        Option.objects.create(name='Accompagnement des enfants')
        k1 = Klass.objects.create(name='1ASSCFEa', section=assc, level=lev1)
        teacher = Teacher.objects.create(
            first_name='Jeanne', last_name='Dupond', birth_date='1974-08-08'
        )

        # Corporation without ext_id will have its ext_id added.
        corp = Corporation.objects.create(name='Centre Cantonal de peinture', city='Marin-Epagnier')
        inst = CorpContact.objects.create(first_name="Roberto", last_name="Rastapopoulos")
        Candidate.objects.create(
            first_name="Bianca", last_name="Castafiore", deposite_date="2018-06-06",
            option='ENF', instructor=inst
        )
        # An existing student, klass should be changed.
        Student.objects.create(ext_id=11111, first_name="Séraphin", last_name="Lampion", city='Marin', klass=k1)
        Student.objects.create(ext_id=44444, first_name="Tryphon", last_name="Tournesol", klass=k1)

        path = os.path.join(os.path.dirname(__file__), 'test_files', 'CLOEE2_Export_FE_2018.xlsx')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-students'), {'upload': fh}, follow=True)
        self.check_form_errors(response)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertIn("La classe '2ASSCFEa' n'existe pas encore", msg)

        klass_assc = Klass.objects.create(name='2ASSCFEa', section=assc, level=lev2)
        klass_epe = Klass.objects.create(
            name='2EDEpe',
            section=Section.objects.create(name='EDE'),
            level=lev2,
        )
        Klass.objects.create(
            name='2EDS18-20',
            section=Section.objects.create(name='EDS'),
            level=lev2,
        )
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-students'), {'upload': fh}, follow=True)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertIn("Objets créés : 2", msg)
        self.assertIn("Objets modifiés : 1", msg)

        # Student already exists, klass changed
        student1 = Student.objects.get(ext_id=11111)
        self.assertEqual(student1.klass.name, '2ASSCFEa')
        self.assertEqual(student1.city, 'Marin')  # file has 'Marin-Epagnier'
        # New student from existing candidate.
        student_cand = Student.objects.get(ext_id=22222)
        self.assertEqual(student_cand.instructor.last_name, 'Rastapopoulos')
        self.assertEqual(student_cand.option_ase.name, 'Accompagnement des enfants')
        self.assertEqual(student_cand.corporation.name, 'Accueil Haut les mains')
        self.assertFalse(student_cand.dispense_eps)
        # Tournesol was archived
        stud_arch = Student.objects.get(ext_id=44444)
        self.assertTrue(stud_arch.archived)
        # Klass teachers have been set
        klass_assc.teacher = teacher
        klass_epe.teacher = teacher
        # Corporation.ext_id is updated
        corp.refresh_from_db()
        self.assertEqual(corp.ext_id, 100)

    def test_import_students_ESTER(self):
        """
        Import CLOEE file for ESTER students (MP_*) version 2018

        Student :
        - S. Lampion, 1MPTS ASE1 - Généraliste
        - B. Castafiore, 1MPTS ASE1

        Export CLOEE:
        - S. Lampion, 2MPTS ASE1 - Accompagnement des enfants
        - T. Tournesol, 2MPS ASSC1

        Results in Student:
        - S. Lampion, 2MPTS ASE1 (Student data + Cloee klass)
        - T. Tournesol, 2MPS ASSC1 (Candidate data + Cloee klass)
        - B. Castafiore, archived
        """
        lev1 = Level.objects.create(name='1')
        lev2 = Level.objects.create(name='2')
        mp_ase = Section.objects.create(name='MP_ASE')
        mp_assc = Section.objects.create(name='MP_ASSC')
        Option.objects.create(name='Accompagnement des enfants')
        Option.objects.create(name='Généraliste')
        k1 = Klass.objects.create(name='1MPTS ASE1', section=mp_ase, level=lev1)
        k2 = Klass.objects.create(name='2MPTS ASE1', section=mp_ase, level=lev2)

        # Existing students, klass should be changed or student archived.
        Student.objects.create(ext_id=11111, first_name="Séraphin", last_name="Lampion", city='Marin', klass=k1)
        Student.objects.create(ext_id=22222, first_name="Bianca", last_name="Castafiore", city='Marin', klass=k1)

        path = os.path.join(os.path.dirname(__file__), 'test_files', 'CLOEE2_Export_Ester_2018.xls')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-students-ester'), {'upload': fh}, follow=True)
        self.check_form_errors(response)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertIn("La classe '2MPS ASSC1' n'existe pas encore", msg)

        k3 = Klass.objects.create(name='2MPS ASSC1', section=mp_assc, level=lev2)
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-students-ester'), {'upload': fh}, follow=True)
        msg = "\n".join(str(m) for m in response.context['messages'])
        self.assertIn("Objets créés : 1", msg)
        self.assertIn("Objets modifiés : 1", msg)

        # Student already existed, klass changed
        student1 = Student.objects.get(ext_id=11111)
        self.assertEqual(student1.klass.name, '2MPTS ASE1')
        self.assertEqual(student1.city, 'Le Locle')
        self.assertEqual(student1.email, 'seraphin.lampion@rpn.ch')
        # Castafiore was archived
        stud_arch = Student.objects.get(ext_id=22222)
        self.assertTrue(stud_arch.archived)

    def test_import_hp(self):
        teacher = Teacher.objects.create(
            first_name='Jeanne', last_name='Dupond', birth_date='1974-08-08'
        )
        path = os.path.join(os.path.dirname(__file__), 'test_files', 'HYPERPLANNING.csv')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-hp'), {'upload': fh}, follow=True)
        self.check_form_errors(response)
        self.assertContains(response, "Objets créés : 13")
        self.assertContains(response, "Objets modifiés : 10")
        self.assertContains(response, "Impossible de trouver «Nom Inconnu» dans la liste des enseignant-e-s")
        self.assertEqual(teacher.course_set.count(), 13)

    def test_import_hp_contacts(self):
        # Those data should have been imported with the student main import file.
        corp = Corporation.objects.create(
            ext_id=44444, name="Crèche Les Mousaillons", typ="Institution", street="Rue des champs 12",
            city="Moulineaux", pcode="2500"
        )
        st1 = Student.objects.create(
            ext_id=164718, first_name='Margot', last_name='Fellmann', birth_date="1994-05-12",
            pcode="2300", city="La Chaux-de-Fonds", corporation=corp)
        Student.objects.create(
            ext_id=53476, first_name='Jojo', last_name='Semaine', birth_date="1997-01-03",
            pcode="2300", city="La Chaux-de-Fonds", corporation=None)

        path = os.path.join(os.path.dirname(__file__), 'test_files', 'Export_HP_Formateurs.xlsx')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(reverse('import-hp-contacts'), {'upload': fh}, follow=True)
        self.check_form_errors(response)
        self.assertContains(response, "Impossible de trouver l&#39;étudiant avec le numéro 10")
        self.assertContains(response, "NoSIRET est vide à ligne 4. Ligne ignorée")
        st1.refresh_from_db()
        self.assertEqual(st1.instructor.last_name, 'Geiser')

    def test_import_and_send_bulletins(self):
        lev1 = Level.objects.create(name='1')
        klass1 = Klass.objects.create(
            name='1ASEFEa',
            section=Section.objects.create(name='ASE'),
            level=lev1,
        )
        Student.objects.bulk_create([
            Student(first_name="Albin", last_name="Dupond", birth_date="1994-05-12", gender='M',
                    pcode="2300", city="La Chaux-de-Fonds", email="albin@example.org",
                    klass=klass1),
            Student(first_name="Justine", last_name="Varrin", birth_date="1994-07-12",
                    pcode="2000", city="Neuchâtel", email="justine@example.org", klass=klass1),
            Student(first_name="Elvire", last_name="Hickx", birth_date="1994-05-20",
                    pcode="2053", city="Cernier", email="elvire@example.org", klass=klass1),
        ])
        path = os.path.join(os.path.dirname(__file__), 'test_files', '1ASEFEa.pdf')
        self.client.login(username='me', password='mepassword')
        with open(path, 'rb') as fh:
            response = self.client.post(
                reverse('import-reports', args=[klass1.pk]),
                data={'upload': fh, 'semester': '1'},
                follow=True
            )
        messages = [str(msg) for msg in response.context['messages']]
        self.assertIn('2 bulletins PDF ont été importés pour la classe 1ASEFEa (sur 3 élèves)', messages)
        student = Student.objects.get(last_name="Dupond")
        self.assertEqual(student.report_sem1.name, 'bulletins/1ASEFEa_1.pdf')

        # Now send
        send_url = reverse('send-student-reports', args=[student.pk, '1'])
        response = self.client.get(send_url)
        data = response.context['form'].initial
        self.assertEqual(data['to'], "albin@example.org")
        response = self.client.post(send_url, data=data, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        # Second email as bcc
        self.assertEqual(mail.outbox[0].recipients(), ['albin@example.org', 'me@example.org'])
        self.assertIn("le bulletin scolaire de Monsieur Albin Dupond", mail.outbox[0].body)
        student.refresh_from_db()
        self.assertIsNotNone(student.report_sem1_sent)
        self.assertIsNone(student.report_sem2_sent)
