import os
import re
import tempfile

from collections import OrderedDict
from datetime import datetime
from fnmatch import fnmatch
from subprocess import PIPE, Popen, call

from tabimport import CSVImportedFile, FileFactory

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.db import IntegrityError, transaction
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from candidats.models import Candidate
from ..forms import StudentImportForm, UploadHPFileForm, UploadReportForm
from ..models import (
    Corporation, CorpContact, Course, Klass, Option, Section, Student, Teacher,
)
from ..utils import is_int


class ImportViewBase(FormView):
    template_name = 'file_import.html'

    @staticmethod
    def _sanitize_date(txt):
        if txt == '':
            return None
        elif isinstance(txt, str):
            return datetime.strptime(txt, '%d.%m.%Y').date()

    def form_valid(self, form):
        upfile = form.cleaned_data['upload']
        is_csv = (
            upfile.name.endswith('.csv') or
            'csv' in upfile.content_type or
            upfile.content_type == 'text/plain'
        )
        try:
            if is_csv:
                # Reopen the file in text mode
                upfile = open(upfile.temporary_file_path(), mode='r', encoding='utf-8-sig')
                imp_file = CSVImportedFile(File(upfile))
            else:
                imp_file = FileFactory(upfile)
            with transaction.atomic():
                stats = self.import_data(imp_file)
        except Exception as e:
            if settings.DEBUG:
                raise
            msg = "L'importation a échoué. Erreur: %s" % e
            if hasattr(upfile, 'content_type'):
                msg += " (content-type: %s)" % upfile.content_type
            messages.error(self.request, msg)
        else:
            non_fatal_errors = stats.get('errors', [])
            if 'created' in stats:
                messages.info(self.request, "Objets créés : %d" % stats['created'])
            if 'modified' in stats:
                messages.info(self.request, "Objets modifiés : %d" % stats['modified'])
            if non_fatal_errors:
                messages.warning(self.request, "Erreurs rencontrées: %s" % "\n".join(non_fatal_errors))
        return HttpResponseRedirect(reverse('admin:index'))


class StudentImportView(ImportViewBase):
    title = "Importation étudiants EPC"
    form_class = StudentImportForm
    # Mapping between column names of a tabular file and Student field names
    student_mapping = {
        'ELE_NUMERO': 'ext_id',
        'ELE_NOM': 'last_name',
        'ELE_PRENOM': 'first_name',
        'ELE_RUE': 'street',
        'ELE_NPA_LOCALITE': 'city',  # pcode is separated from city in prepare_import
        'ELE_CODE_CANTON': 'district',
        'ELE_TEL_PRIVE': 'tel',
        'ELE_TEL_MOBILE': 'mobile',
        'ELE_EMAIL_RPN': 'email',
        'ELE_COMPTE_RPN': 'login_rpn',
        'ELE_DATE_NAISSANCE': 'birth_date',
        'ELE_AVS': 'avs',
        'ELE_SEXE': 'gender',
        'INS_CLASSE': 'klass',
        'INS_MC': 'teacher',
        'PROF_DOMAINE_SPEC': 'option_ase',
    }
    corporation_mapping = {
        'ENT_NUMERO' : 'ext_id',
        'ENT_NOM' : 'name',
        'ENT_RUE': 'street',
        'ENT_NPA': 'pcode',
        'ENT_LOCALITE': 'city',
        'ENT_TEL': 'tel',
        'ENT_CODE_CANTON': 'district',
    }
    mapping_option_ase = {
        'GEN': 'Généraliste',
        'Enfants': 'Accompagnement des enfants',
        'ENF': 'Accompagnement des enfants',
        'HAN': 'Accompagnement des personnes handicapées',
        'PAG': 'Accompagnement des personnes âgées',
    }
    # Those values are always taken from the import file
    fields_to_overwrite = ['klass', 'district', 'login_rpn']
    klasses_to_skip = []

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'file_label': 'Fichier des étudiants',
            'mandatory_headers': self.student_mapping.keys(),
        })
        return kwargs

    def clean_values(self, values):
        """Post-process some of the imported values."""
        if 'birth_date' in values:
            values['birth_date'] = self._sanitize_date(values['birth_date'])
        # See if postal code included in city, and split them
        if 'city' in values and is_int(values['city'][:4]):
            values['pcode'], _, values['city'] = values['city'].partition(' ')

        if 'klass' in values:
            try:
                k = Klass.objects.get(name=values['klass'])
            except Klass.DoesNotExist:
                raise Exception("La classe '%s' n'existe pas encore" % values['klass'])
            values['klass'] = k

        if 'option_ase' in values:
            if values['option_ase']:
                try:
                    values['option_ase'] = Option.objects.get(name=values['option_ase'])
                except Option.DoesNotExist:
                    values['option_ase'] = None
            else:
                values['option_ase'] = None
        return values

    @property
    def _existing_students(self):
        return Student.objects.filter(
            archived=False,
            ext_id__isnull=False,
            klass__section__in=[s for s in Section.objects.all() if s.is_EPC]
        )

    def update_defaults_from_candidate(self, defaults):
        # Any DoesNotExist exception will bubble up.
        candidate = Candidate.objects.get(last_name=defaults['last_name'],
                                          first_name=defaults['first_name'])
        # Mix CLOEE data and Candidate data
        if candidate.option in self.mapping_option_ase:
            defaults['option_ase'] = Option.objects.get(name=self.mapping_option_ase[candidate.option])
        if candidate.corporation:
            defaults['corporation'] = candidate.corporation
        defaults['instructor'] = candidate.instructor
        defaults['dispense_ecg'] = candidate.exemption_ecg
        defaults['soutien_dys'] = candidate.handicap

    def import_data(self, up_file):
        """ Import Student data from uploaded file. """

        def strip(val):
            return val.strip() if isinstance(val, str) else val

        obj_created = obj_modified = 0
        err_msg = []
        seen_students_ids = set()
        existing_students_ids = set(
            self._existing_students.values_list('ext_id', flat=True)
        )
        seen_klasses = set()
        prof_dict = {str(t): t for t in Teacher.objects.all()}

        for line in up_file:
            student_defaults = {
                val: strip(line[key]) for key, val in self.student_mapping.items()
            }
            if student_defaults['ext_id'] in seen_students_ids:
                # Second line for student, ignore it
                continue
            for klass in self.klasses_to_skip:
                if fnmatch(student_defaults['klass'], klass):
                    continue
            seen_students_ids.add(student_defaults['ext_id'])

            if self.corporation_mapping:
                corporation_defaults = {
                    val: strip(line[key]) for key, val in self.corporation_mapping.items()
                }
                student_defaults['corporation'] = self.get_corporation(corporation_defaults)

            if 'option_ase' in self.fields_to_overwrite:
                if student_defaults['option_ase'] in self.mapping_option_ase:
                    student_defaults['option_ase'] = self.mapping_option_ase[student_defaults['option_ase']]

            defaults = self.clean_values(student_defaults)

            if defaults.get('teacher') and defaults['klass'] not in seen_klasses:
                klass = defaults['klass']
                for full_name in defaults['teacher'].split(', '):
                    if 'Secrétariat' in full_name:
                        continue
                    # Set the teacher for this klass
                    try:
                        klass.teacher = prof_dict[full_name]
                        klass.save()
                    except KeyError:
                        err_msg.append(
                            "L'enseignant {0} n'existe pas dans la base de données".format(full_name)
                        )
                    seen_klasses.add(klass)

            try:
                student = Student.objects.get(ext_id=defaults['ext_id'])
                modified = False
                for field_name in self.fields_to_overwrite:
                    if getattr(student, field_name) != defaults[field_name]:
                        setattr(student, field_name, defaults[field_name])
                        modified = True
                if student.archived:
                    student.archived = False
                    modified = True
                if modified:
                    student.save()
                    obj_modified += 1
            except Student.DoesNotExist:
                try:
                    self.update_defaults_from_candidate(defaults)
                except Candidate.DoesNotExist:
                    # New student with no matching Candidate
                    err_msg.append('Étudiant non trouvé dans les candidats: {0} {1} - classe: {2}'.format(
                        defaults['last_name'],
                        defaults['first_name'],
                        defaults['klass'])
                    )

                defaults.pop('teacher', None)
                Student.objects.create(**defaults)
                obj_created += 1

        # Archive students who have not been exported
        rest = existing_students_ids - seen_students_ids
        archived = 0
        for student_id in rest:
            st = Student.objects.get(ext_id=student_id)
            st.archived = True
            st.save()
            archived += 1
        return {
            'created': obj_created, 'modified': obj_modified, 'archived': archived,
            'errors': err_msg,
        }

    def get_corporation(self, corp_values):
        if corp_values['ext_id'] == '':
            return None
        if 'city' in corp_values and is_int(corp_values['city'][:4]):
            corp_values['pcode'], _, corp_values['city'] = corp_values['city'].partition(' ')
        try:
            corp, created = Corporation.objects.get_or_create(
                ext_id=corp_values['ext_id'],
                defaults=corp_values
            )
        except IntegrityError:
            # It may happen that the corporation exists (name and city are enforced unique)
            # but without the ext_id. In that case, we update the ext_id.
            try:
                corp = Corporation.objects.get(name=corp_values['name'], city=corp_values['city'])
                if corp.ext_id:
                    raise
                corp.ext_id = corp_values['ext_id']
                corp.save()
            except Corporation.DoesNotExist:
                raise
        return corp


class StudentEsterImportView(StudentImportView):
    title = "Importation étudiants ESTER"
    # Mapping between column names of a tabular file and Student field names
    student_mapping = {
        'ELE_NUMERO': 'ext_id',
        'ELE_NOM': 'last_name',
        'ELE_PRENOM': 'first_name',
        'ELE_RUE': 'street',
        'ELE_NPA_LOCALITE': 'city',  # pcode is separated from city in prepare_import
        'ELE_DATE_NAISSANCE': 'birth_date',
        'ELE_AVS': 'avs',
        'ELE_SEXE': 'gender',
        'INS_CLASSE': 'klass',
        'ELE_CODE_CANTON': 'district',
        'ELE_TEL_PRIVE': 'tel',
        'ELE_TEL_MOBILE': 'mobile',
        'ELE_EMAIL_RPN': 'email',
        'ELE_COMPTE_RPN': 'login_rpn',
        # 'PROF_DOMAINE_SPEC': 'option_ase',
    }
    corporation_mapping = None
    # Those values are always taken from the import file
    fields_to_overwrite = ['klass', 'street', 'city','district', 'tel', 'mobile', 'email', 'login_rpn']
    klasses_to_skip = ['1CMS*']  # Abandon classes 1CMS ASE + 1CMS ASSC

    @property
    def _existing_students(self):
        return Student.objects.filter(
            archived=False,
            ext_id__isnull=False,
            klass__section__in=[s for s in Section.objects.all() if s.is_ESTER]
        )

    def update_defaults_from_candidate(self, defaults):
        pass


class HPImportView(ImportViewBase):
    """
    Importation du fichier HyperPlanning pour l'établissement  des feuilles
    de charges.
    """
    form_class = UploadHPFileForm
    mapping = {
        'NOMPERSO_ENS': 'teacher',
        'LIBELLE_MAT': 'subject',
        'NOMPERSO_DIP': 'public',
        'TOTAL': 'period',
    }
    # Mapping between klass field and imputation
    account_categories = OrderedDict([
        ('ASAFE', 'ASAFE'),
        ('ASEFE', 'ASEFE'),
        ('ASSCFE', 'ASSCFE'),

        ('#Mandat_ASA', 'ASAFE'),

        ('MPTS', 'MPTS'),
        ('MPS', 'MPS'),
        ('CMS ASE', 'MPTS'),
        ('CMS ASSC', 'MPS'),

        ('EDEpe', 'EDEpe'),
        ('EDEps', 'EDEps'),
        ('EDS', 'EDS'),
        ('CAS_FPP', 'CAS_FPP'),

        # To split afterwards
        ('EDE', 'EDE'),
        ('#Mandat_ASE', 'ASE'),
        ('#Mandat_ASSC', 'ASSC'),
    ])

    def import_data(self, up_file):
        obj_created = obj_modified = 0
        errors = []

        # Pour accélérer la recherche
        profs = {str(t): t for t in Teacher.objects.all()}
        Course.objects.all().delete()

        for line in up_file:
            if (line['LIBELLE_MAT'] == '' or line['NOMPERSO_DIP'] == '' or line['TOTAL'] == ''):
                continue

            try:
                teacher = profs[line['NOMPERSO_ENS']]
            except KeyError:
                errors.append(
                    "Impossible de trouver «%s» dans la liste des enseignant-e-s" % line['NOMPERSO_ENS']
                )
                continue

            obj, created = Course.objects.get_or_create(
                teacher=teacher,
                subject=line['LIBELLE_MAT'],
                public=line['NOMPERSO_DIP'],
            )

            period = int(float(line['TOTAL'].replace("'", "")))
            if created:
                obj.period = period
                obj_created += 1
                for k, v in self.account_categories.items():
                    if k in obj.public:
                        obj.imputation = v
                        break
            else:
                obj.period += period
                obj_modified += 1
            obj.save()

            if not obj.imputation:
                errors.append("Le cours {0} n'a pas pu être imputé correctement!". format(str(obj)))

        return {'created': obj_created, 'modified': obj_modified, 'errors': errors}


class HPContactsImportView(ImportViewBase):
    """
    Importation du fichier Hyperplanning contenant les formateurs d'étudiants.
    """
    form_class = UploadHPFileForm

    def import_data(self, up_file):
        obj_modified = 0
        errors = []
        for idx, line in enumerate(up_file, start=2):
            try:
                student = Student.objects.get(ext_id=int(line['UID_ETU']))
            except Student.DoesNotExist:
                errors.append(
                    "Impossible de trouver l'étudiant avec le numéro %s" % int(line['UID_ETU'])
                )
                continue
            if not line['NoSIRET']:
                errors.append(
                    "NoSIRET est vide à ligne %d. Ligne ignorée" % idx
                )
                continue
            try:
                corp = Corporation.objects.get(ext_id=int(line['NoSIRET']))
            except Corporation.DoesNotExist:
                errors.append(
                    "Impossible de trouver l'institution avec le numéro %s" % int(line['NoSIRET'])
                )
                continue

            # Check corporation matches
            if student.corporation_id != corp.pk:
                # This import has priority over the corporation set by StudentImportView
                student.corporation = corp
                student.save()

            contact = corp.corpcontact_set.filter(
                first_name__iexact=line['PRENOMMDS'].strip(),
                last_name__iexact=line['NOMMDS'].strip()
            ).first()
            if contact is None:
                contact = CorpContact.objects.create(
                    corporation=corp, first_name=line['PRENOMMDS'].strip(),
                    last_name=line['NOMMDS'].strip(), civility=line['CIVMDS'], email=line['EMAILMDS']
                )
            else:
                if line['CIVMDS'] and contact.civility != line['CIVMDS']:
                    contact.civility = line['CIVMDS']
                    contact.save()
                if line['EMAILMDS'] and contact.email != line['EMAILMDS']:
                    contact.email = line['EMAILMDS']
                    contact.save()
            if student.instructor != contact:
                student.instructor = contact
                student.save()
                obj_modified += 1
        return {'modified': obj_modified, 'errors': errors}


class ImportReportsView(FormView):
    template_name = 'file_import.html'
    form_class = UploadReportForm

    def dispatch(self, request, *args, **kwargs):
        self.klass = get_object_or_404(Klass, pk=kwargs['pk'])
        self.title = "Importation d'un fichier PDF de moyennes pour la classe {}".format(self.klass.name)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        upfile = form.cleaned_data['upload']
        klass_name = upfile.name[:-4]
        redirect_url = reverse('class', args=[self.klass.pk])

        if self.klass.name != klass_name:
            messages.error(
                self.request,
                "Le fichier téléchargé ne correspond pas à la classe {} !".format(self.klass.name)
            )
            return HttpResponseRedirect(redirect_url)

        # Check poppler-utils presence on server
        res = call(['pdftotext', '-v'], stderr=PIPE)
        if res != 0:
            messages.error(
                self.request,
                "Unable to find pdftotext on your system. Try to install the poppler-utils package."
            )
            return HttpResponseRedirect(redirect_url)

        # Move the file to MEDIA directory
        pdf_origin = os.path.join(settings.MEDIA_ROOT, upfile.name)
        with open(pdf_origin, 'wb+') as destination:
            for chunk in upfile.chunks():
                destination.write(chunk)

        try:
            self.import_reports(pdf_origin, form.cleaned_data['semester'])
        except Exception as err:
            raise
            if settings.DEBUG:
                raise
            else:
                messages.error(self.request, "Erreur durant l'importation des bulletins PDF: %s" % err)
        return HttpResponseRedirect(redirect_url)

    def import_reports(self, pdf_path, semester):
        path = os.path.abspath(pdf_path)
        student_regex = '[E|É]lève\s*:\s*([^\n]*)'
        # Directory automatically deleted when the variable is deleted
        _temp_dir = tempfile.TemporaryDirectory()
        temp_dir = _temp_dir.name

        os.system("pdfseparate %s %s/%s_%%d.pdf" % (path, temp_dir, os.path.basename(path)[:-4]))

        # Look for student names in each separated PDF and rename PDF with student name
        pdf_count = 0
        pdf_field = 'report_sem' + semester
        for filename in os.listdir(temp_dir):
            p = Popen(['pdftotext', os.path.join(temp_dir, filename), '-'],
                      shell=False, stdout=PIPE, stderr=PIPE)
            output, errs = p.communicate()
            m = re.search(student_regex, output.decode('utf-8'))
            if not m:
                print("Unable to find student name in %s" % filename)
                continue
            student_name = m.groups()[0]
            # Find a student with the found student_name
            try:
                student = self.klass.student_set.exclude(archived=True
                    ).annotate(fullname=Concat('last_name', Value(' '), 'first_name')).get(fullname=student_name)
            except Student.DoesNotExist:
                messages.warning(
                    self.request,
                    "Impossible de trouver l'étudiant {} dans la classe {}".format(student_name, self.klass.name)
                )
                continue
            with open(os.path.join(temp_dir, filename), 'rb') as pdf:
                getattr(student, pdf_field).save(filename, File(pdf), save=True)
            student.save()
            pdf_count += 1

        messages.success(
            self.request,
            '{0} bulletins PDF ont été importés pour la classe {1} (sur {2} élèves)'.format(
                pdf_count, self.klass.name,
                self.klass.student_set.exclude(archived=True).count()
            )
        )
