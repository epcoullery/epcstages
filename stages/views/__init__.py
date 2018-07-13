import json
import os
import re
from subprocess import PIPE, Popen, call

import tempfile
from collections import OrderedDict
from datetime import date, datetime, timedelta

from tabimport import CSVImportedFile, FileFactory

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Count, Value, Q, Sum
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateformat import format as django_format
from django.utils.translation import ugettext as _
from django.utils.text import slugify
from django.views.generic import DetailView, FormView, TemplateView, ListView

from .base import EmailConfirmationBaseView, ZippedFilesBaseView
from .export import OpenXMLExport
from ..forms import EmailBaseForm, PeriodForm, StudentImportForm, UploadHPFileForm, UploadReportForm
from ..models import (
    Klass, Section, Option, Student, Teacher, Corporation, CorpContact, Course, Period,
    Training, Availability
)
from candidats.models import Candidate
from ..pdf import (
    ChargeSheetPDF, ExpertEdeLetterPdf, UpdateDataFormPDF, MentorCompensationPdfForm,
    KlassListPDF,
)
from ..utils import is_int, school_year_start




class CorporationListView(ListView):
    model = Corporation
    template_name = 'corporations.html'


class CorporationView(DetailView):
    model = Corporation
    template_name = 'corporation.html'
    context_object_name = 'corp'

    def get_context_data(self, **kwargs):
        context = super(CorporationView, self).get_context_data(**kwargs)
        # Create a structure like:
        #   {'2011-2012': {'avails': [avail1, avail2, ...], 'stats': {'fil': num}},
        #    '2012-2013': ...}
        school_years = OrderedDict()
        for av in Availability.objects.filter(corporation=self.object
                ).select_related('training__student__klass', 'period__section'
                ).order_by('period__start_date'):
            if av.period.school_year not in school_years:
                school_years[av.period.school_year] = {'avails': [], 'stats': {}}
            school_years[av.period.school_year]['avails'].append(av)
            if av.period.section.name not in school_years[av.period.school_year]['stats']:
                school_years[av.period.school_year]['stats'][av.period.section.name] = 0
            try:
                av.training
                # Only add to stats if training exists
                school_years[av.period.school_year]['stats'][av.period.section.name] += av.period.weeks
            except Training.DoesNotExist:
                pass

        context['years'] = school_years
        return context


class KlassListView(ListView):
    queryset = Klass.active.order_by('section', 'name')
    template_name = 'classes.html'


class KlassView(DetailView):
    model = Klass
    template_name = 'class.html'
    context_object_name = 'klass'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = self.object.student_set.filter(archived=False
            ).prefetch_related('training_set').order_by('last_name', 'first_name')
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') != 'xls':
            return super().render_to_response(context, **response_kwargs)

        export = OpenXMLExport(self.object.name)
        # Headers
        export.write_line([
            'Nom', 'Prénom', 'Domicile', 'Date de naissance',
            'Stage 1', 'Domaine 1', 'Stage 2', 'Domaine 2', 'Stage 3', 'Domaine 3',
        ], bold=True, col_widths=[18, 15, 20, 14, 25, 12, 25, 12, 25, 12])
        # Data
        for student in context['students']:
            values = [
                student.last_name, student.first_name,
                " ".join([student.pcode, student.city]), student.birth_date,
            ]
            for training in student.training_set.select_related(
                        'availability', 'availability__corporation', 'availability__domain'
                    ).all():
                values.append(training.availability.corporation.name)
                values.append(training.availability.domain.name)
            export.write_line(values)

        return export.get_http_response('%s_export' % self.object.name.replace(' ', '_'))


class AttributionView(TemplateView):
    """
    Base view for the attribution screen. Populate sections and referents.
    All other data are retrieved through AJAX requests:
      * training periods: section_period
      * corp. availabilities for current period: period_availabilities
      * already planned training for current period: TrainingsByPeriodView
      * student list targetted by current period: period_students
    When an availability is chosen:
      * corp. contact list: CorpContactJSONView
    When a student is chosen;
      * details of a student: StudentSummaryView
    """
    template_name = 'attribution.html'

    def get_context_data(self, **kwargs):
        context = super(AttributionView, self).get_context_data(**kwargs)
        # Need 2 queries, because referents with no training item would not appear in the second query
        referents = Teacher.objects.filter(archived=False).order_by('last_name', 'first_name')

        # Populate each referent with the number of referencies done during the current school year
        ref_counts = dict([(ref.id, ref.num_refs)
                for ref in Teacher.objects.filter(archived=False, training__availability__period__end_date__gte=school_year_start()
                ).annotate(num_refs=Count('training'))])
        for ref in referents:
            ref.num_refs = ref_counts.get(ref.id, 0)

        context.update({
            #'period_form': PeriodForm(),
            'sections': Section.objects.filter(name__startswith='MP'),
            'referents': referents,
        })
        return context


class StudentSummaryView(DetailView):
    model = Student
    template_name = 'student_summary.html'

    def get_context_data(self, **kwargs):
        context = super(StudentSummaryView, self).get_context_data(**kwargs)
        context['previous_stages'] = self.object.training_set.all(
            ).select_related('availability__corporation').order_by('availability__period__end_date')
        period_id = self.request.GET.get('period')
        if period_id:
            try:
                period = Period.objects.get(pk=int(period_id))
            except Period.DoesNotExist:
                pass
            else:
                context['age_for_stage'] = self.object.age_at(period.start_date)
                context['age_style'] = 'under_17' if (int(context['age_for_stage'].split()[0]) < 17) else ''
        return context


class AvailabilitySummaryView(DetailView):
    model = Availability
    template_name = 'availability_summary.html'


class TrainingsByPeriodView(ListView):
    template_name = 'trainings_list.html'
    context_object_name = 'trainings'

    def get_queryset(self):
        return Training.objects.select_related('student__klass', 'availability__corporation', 'availability__domain'
            ).filter(availability__period__pk=self.kwargs['pk']
            ).order_by('student__last_name', 'student__first_name')


class CorpContactJSONView(ListView):
    """ Return all contacts from a given corporation """
    return_fields = ['id', 'first_name', 'last_name', 'role', 'is_main']

    def get_queryset(self):
        return CorpContact.objects.filter(corporation__pk=self.kwargs['pk'], archived=False)

    def render_to_response(self, context):
        serialized = [dict([(field, getattr(obj, field)) for field in self.return_fields])
                      for obj in context['object_list']]
        return HttpResponse(json.dumps(serialized), content_type="application/json")

# AJAX views:

def section_periods(request, pk):
    """ Return all periods (until 2 years ago) from a section (JSON) """
    section = get_object_or_404(Section, pk=pk)
    two_years_ago = datetime.now() - timedelta(days=365 * 2)
    periods = [{'id': p.id, 'dates': p.dates, 'title': p.title}
               for p in section.period_set.filter(start_date__gt=two_years_ago).order_by('-start_date')]
    return HttpResponse(json.dumps(periods), content_type="application/json")

def section_classes(request, pk):
    section = get_object_or_404(Section, pk=pk)
    classes = [(k.id, k.name) for k in section.klass_set.all()]
    return HttpResponse(json.dumps(classes), content_type="application/json")


def period_students(request, pk):
    """
    Return all active students from period's section and level,
    with corresponding Training if existing (JSON)
    """
    period = get_object_or_404(Period, pk=pk)
    students = Student.objects.filter(
        archived=False, klass__section=period.section, klass__level=period.relative_level
        ).order_by('last_name')
    trainings = dict((t.student_id, t.id) for t in Training.objects.filter(availability__period=period))
    data = [{
        'name': str(s),
        'id': s.id,
        'training_id': trainings.get(s.id),
        'klass': s.klass.name} for s in students]
    return HttpResponse(json.dumps(data), content_type="application/json")

def period_availabilities(request, pk):
    """ Return all availabilities in the specified period """
    period = get_object_or_404(Period, pk=pk)
    # Sorting by the boolean priority is first with PostgreSQL, last with SQLite :-/
    corps = [{'id': av.id, 'id_corp': av.corporation.id, 'corp_name': av.corporation.name,
              'domain': av.domain.name, 'free': av.free, 'priority': av.priority}
             for av in period.availability_set.select_related('corporation').all(
                                             ).order_by('-priority', 'corporation__name')]
    return HttpResponse(json.dumps(corps), content_type="application/json")

def new_training(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    ref_key = request.POST.get('referent')
    cont_key = request.POST.get('contact')
    try:
        ref = Teacher.objects.get(pk=ref_key) if ref_key else None
        contact = CorpContact.objects.get(pk=cont_key) if cont_key else None
        avail = Availability.objects.get(pk=request.POST.get('avail'))
        training = Training.objects.create(
            student=Student.objects.get(pk=request.POST.get('student')),
            availability=avail,
            referent=ref,
        )
        if avail.contact != contact:
            avail.contact = contact
            avail.save()
    except Exception as exc:
        return HttpResponse(str(exc))
    return HttpResponse(b'OK')

def del_training(request):
    """ Delete training and return the referent id """
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    training = get_object_or_404(Training, pk=request.POST.get('pk'))
    ref_id = training.referent_id
    training.delete()
    return HttpResponse(json.dumps({'ref_id': ref_id}), content_type="application/json")


class ImportViewBase(FormView):
    template_name = 'file_import.html'

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


def _import_date(txt):
    if txt == '':
        return None
    elif isinstance(txt, str):
        return datetime.strptime(txt, '%d.%m.%Y').date()

def _import_option_ase(txt=None):
    if txt:
        try:
            return Option.objects.get(name=txt)
        except Option.DoesNotExist:
            return None
    else:
        return None


class StudentFeImportView_2018(ImportViewBase):
    """
    Import CLOEE file for FE students (ASAFE, ASEFE, ASSCFE, EDE, EDS)
    Some students may appear twice
    """

    title = "Importation étudiants FE"
    form_class = StudentImportForm

    def import_data(self, up_file):
        """ Import Student data from uploaded file. """
        student_mapping = settings.STUDENT_IMPORT_2018_MAPPING
        student_rev_mapping = {v: k for k, v in student_mapping.items()}
        corporation_mapping = settings.CORPORATION_IMPORT_2018_MAPPING
        instructor_mapping = settings.INSTRUCTOR_IMPORT_2018_MAPPING
        mapping_option_ase = {
            'GEN': 'Généraliste',
            'ENF': 'Accompagnement des enfants',
            'HAN': 'Accompagnement des personnes handicapées',
            'PAG': 'Accompagnement des personnes âgées'
        }
        def strip(val):
            return val.strip() if isinstance(val, str) else val

        obj_created = obj_modified = obj_error = 0
        seen_students_ids = set()
        old_students_ids = {x['ext_id'] for x in Student.objects.all().values('ext_id')}
        err_msg = list()

        for line in up_file:
            student_defaults = {
                val: strip(line[key]) for key, val in student_mapping.items()
            }
            if student_defaults['ext_id'] in seen_students_ids:
                # Second line for student, ignore it
                continue
            seen_students_ids.add(student_defaults['ext_id'])

            student_defaults['birth_date'] = _import_date(student_defaults['birth_date'])
            student_defaults['option_ase'] = _import_option_ase(student_defaults['option_ase'])
            if student_defaults['option_ase'] is None:
                del student_defaults['option_ase']

            corporation_defaults = {
                val: strip(line[key]) for key, val in corporation_mapping.items()
            }
            student_defaults['corporation'] = self.get_corporation(corporation_defaults)

            defaults = Student.prepare_import(student_defaults)
            try:
                student = Student.objects.get(ext_id=defaults['ext_id'])
                # Replace only klass and login by CLOEE data
                student.klass = defaults['klass']
                student.login_rpn = defaults['login_rpn']
                student.archived = False
                student.save()
                obj_modified += 1
            except Student.DoesNotExist:
                # Is student in candidates table ?
                try:
                    candidate = Candidate.objects.get(last_name=defaults['last_name'],
                                                      first_name=defaults['first_name'])
                    # Mix CLOEE data and Candidate data
                    if candidate.option in mapping_option_ase:
                        defaults['option_ase'] = Option.objects.get(name=mapping_option_ase[candidate.option])
                    defaults['corporation'] = candidate.corporation
                    defaults['instructor'] = candidate.instructor
                    defaults['dispense_ecg'] = candidate.exemption_ecg
                    defaults['soutien_dys'] = candidate.handicap
                    defaults['archived'] = False
                    Student.objects.create(**defaults)
                    obj_created += 1
                except Candidate.DoesNotExist:
                    obj_error += 1
                    err_msg.append('Etudiant inconnu: {0} {1} - classe: {2}'.format(
                            defaults['last_name'],
                            defaults['first_name'],
                            defaults['klass'])
                    )
                    Student.objects.create(**defaults)

        # Archive students who have not been exported
        rest = old_students_ids - seen_students_ids
        for item in rest:
            st = Student.objects.get(ext_id=item)
            st.archived = True
            st.save()

        # FIXME: implement arch_staled
        return {'created': obj_created, 'modified': obj_modified, 'error': obj_error, 'errors': err_msg}

    def get_corporation(self, corp_values):
        if corp_values['ext_id'] == '':
            return None
        if 'city' in corp_values and is_int(corp_values['city'][:4]):
            corp_values['pcode'], _, corp_values['city'] = corp_values['city'].partition(' ')
        corp, created = Corporation.objects.get_or_create(
            ext_id=corp_values['ext_id'],
            defaults=corp_values
        )
        return corp


class StudentImportView(ImportViewBase):
    title = "Importation étudiants"
    form_class = StudentImportForm

    def import_data(self, up_file):
        """ Import Student data from uploaded file. """
        student_mapping = settings.STUDENT_IMPORT_MAPPING
        student_rev_mapping = {v: k for k, v in student_mapping.items()}
        corporation_mapping = settings.CORPORATION_IMPORT_MAPPING
        instructor_mapping = settings.INSTRUCTOR_IMPORT_MAPPING

        def strip(val):
            return val.strip() if isinstance(val, str) else val

        obj_created = obj_modified = 0
        seen_students_ids = set()
        for line in up_file:
            student_defaults = {
                val: strip(line[key]) for key, val in student_mapping.items()
            }
            if student_defaults['ext_id'] in seen_students_ids:
                # Second line for student, ignore it
                continue
            seen_students_ids.add(student_defaults['ext_id'])
            if student_defaults['birth_date'] == '':
                student_defaults['birth_date'] = None
            elif isinstance(student_defaults['birth_date'], str):
                student_defaults['birth_date'] = datetime.strptime(student_defaults['birth_date'], '%d.%m.%Y').date()
            if student_defaults['option_ase']:
                try:
                    student_defaults['option_ase'] = Option.objects.get(name=student_defaults['option_ase'])
                except Option.DoesNotExist:
                    del student_defaults['option_ase']
            else:
                del student_defaults['option_ase']

            corporation_defaults = {
                val: strip(line[key]) for key, val in corporation_mapping.items()
            }
            student_defaults['corporation'] = self.get_corporation(corporation_defaults)

            defaults = Student.prepare_import(student_defaults)
            try:
                student = Student.objects.get(ext_id=student_defaults['ext_id'])
                modified = False
                for key, val in defaults.items():
                    if getattr(student, key) != val:
                        setattr(student, key, val)
                        modified = True
                if modified:
                    student.save()
                    obj_modified += 1
            except Student.DoesNotExist:
                student = Student.objects.create(**defaults)
                obj_created += 1
        # FIXME: implement arch_staled
        return {'created': obj_created, 'modified': obj_modified}

    def get_corporation(self, corp_values):
        if corp_values['ext_id'] == '':
            return None
        if 'city' in corp_values and is_int(corp_values['city'][:4]):
            corp_values['pcode'], _, corp_values['city'] = corp_values['city'].partition(' ')
        corp, created = Corporation.objects.get_or_create(
            ext_id=corp_values['ext_id'],
            defaults=corp_values
        )
        return corp


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

            period = int(float(line['TOTAL'].replace("'","")))
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
            messages.error(self.request,
                "Le fichier téléchargé ne correspond pas à la classe {} !".format(self.klass.name)
            )
            return HttpResponseRedirect(redirect_url)

        # Check poppler-utils presence on server
        res = call(['pdftotext', '-v'], stderr=PIPE)
        if res != 0:
            messages.error(self.request, "Unable to find pdftotext on your system. Try to install the poppler-utils package.")
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


class SendStudentReportsView(FormView):
    template_name = 'email_report.html'
    form_class = EmailBaseForm

    def get_initial(self):
        initial = super().get_initial()
        self.student = Student.objects.get(pk=self.kwargs['pk'])
        self.semestre = self.kwargs['semestre']

        to = [self.student.email]
        if self.student.instructor and self.student.instructor.email:
            to.append(self.student.instructor.email)

        context = {
            'student': self.student,
            'sender': self.request.user,
        }

        initial.update({
            'cci': self.request.user.email,
            'to': '; '.join(to),
            'subject': "Bulletin semestriel",
            'message': loader.render_to_string('email/bulletins_scolaires.txt', context),
            'sender': self.request.user.email,
        })
        return initial

    def form_valid(self, form):
        email = EmailMessage(
            subject=form.cleaned_data['subject'],
            body=form.cleaned_data['message'],
            from_email=form.cleaned_data['sender'],
            to=form.cleaned_data['to'].split(';'),
            bcc=form.cleaned_data['cci'].split(';'),
        )
        # Attach PDF file to email
        student_filename = slugify('{0} {1}'.format(self.student.last_name, self.student.first_name))
        student_filename = '{0}.pdf'.format(student_filename)
        # pdf_file = os.path.join(dir_klass, pdf_file_list[attach_idx])
        pdf_name = 'bulletin_scol_{0}'.format(student_filename)
        with open(getattr(self.student, 'report_sem%d' % self.semestre).path, 'rb') as pdf:
            email.attach(pdf_name, pdf.read(), 'application/pdf')

        try:
            email.send()
        except Exception as err:
            messages.error(self.request, "Échec d’envoi pour l'étudiant {0} ({1})".format(self.student, err))
        else:
            setattr(self.student, 'report_sem%d_sent' % self.semestre, timezone.now())
            self.student.save()
            messages.success(self.request, "Le message a été envoyé.")
        return HttpResponseRedirect(reverse('class', args=[self.student.klass.pk]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'candidat': self.student,
            'title': 'Envoi du bulletin semestriel',
            'pdf_field': getattr(self.student, 'report_sem%d' % self.semestre),
        })
        return context


class EmailConfirmationView(EmailConfirmationBaseView):
    person_model = Student
    success_url = reverse_lazy('admin:stages_student_changelist')
    error_message = "Échec d’envoi pour l’étudiant {person} ({err})"


class StudentConvocationExaminationView(EmailConfirmationView):
    success_message = "Le message de convocation a été envoyé pour l’étudiant {person}"
    title = "Convocation à la soutenance du travail de diplôme"

    def dispatch(self, request, *args, **kwargs):
        self.student = Student.objects.get(pk=self.kwargs['pk'])
        errors = self.student.missing_examination_data()
        if self.student.expert and not self.student.expert.email:
            errors.append("L’expert externe n’a pas de courriel valide !")
        if self.student.internal_expert and not self.student.internal_expert.email:
            errors.append("L’expert interne n'a pas de courriel valide !")
        if self.student.date_soutenance_mailed is not None:
            errors.append("Une convocation a déjà été envoyée !")
        if errors:
            messages.error(request, "\n".join(errors))
            return redirect(reverse("admin:stages_student_change", args=(self.student.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        to = [self.student.email, self.student.expert.email, self.student.internal_expert.email]
        src_email = 'email/student_convocation_EDE.txt'

        # Recipients with ladies first!
        recip_names = sorted([
            self.student.civility_full_name,
            self.student.expert.civility_full_name,
            self.student.internal_expert.civility_full_name,
        ])
        titles = [
            self.student.civility,
            self.student.expert.civility,
            self.student.internal_expert.civility,
        ]
        mme_count = titles.count('Madame')
        # Civilities, with ladies first!
        if mme_count == 0:
            civilities = 'Messieurs'
        elif mme_count == 1:
            civilities = 'Madame, Messieurs'
        elif mme_count == 2:
            civilities = 'Mesdames, Monsieur'
        else:
            civilities = 'Mesdames'

        msg_context = {
            'recipient1': recip_names[0],
            'recipient2': recip_names[1],
            'recipient3': recip_names[2],
            'student': self.student,
            'sender': self.request.user,
            'global_civilities': civilities,
            'date_examen': django_format(self.student.date_exam, 'l j F Y à H\hi'),
            'salle': self.student.room,
        }
        initial.update({
            'cci': self.request.user.email,
            'to': '; '.join(to),
            'subject': "Convocation à la soutenance de travail de diplôme",
            'message': loader.render_to_string(src_email, msg_context),
            'sender': self.request.user.email,
        })
        return initial

    def on_success(self, student):
        student.date_soutenance_mailed = timezone.now()
        student.save()


class PrintUpdateForm(ZippedFilesBaseView):
    """
    PDF form to update personal data
    """
    filename = 'modification.zip'

    def get(self, request, *args, **kwargs):
        try:
            self.return_date = date(*reversed([int(num) for num in self.request.GET.get('date').split('.')]))
        except (AttributeError, ValueError):
            messages.error(request, "La date fournie n'est pas valable")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().get(request, *args, **kwargs)

    def generate_files(self):
        for klass in Klass.objects.filter(level__gte=2
                ).exclude(section__name='MP_ASSC').exclude(section__name='MP_ASE'):
            pdf = UpdateDataFormPDF('{0}.pdf'.format(klass.name), self.return_date)
            pdf.produce(klass)
            yield pdf.filename


def print_expert_ede_compensation_form(request, pk):
    """
    Imprime le PDF à envoyer à l'expert EDE en accompagnement du
    travail de diplôme
    """
    student = Student.objects.get(pk=pk)
    missing = student.missing_examination_data()
    if missing:
        messages.error(request, "\n".join(
            ["Toutes les informations ne sont pas disponibles pour la lettre à l’expert!"]
            + missing
        ))
        return redirect(reverse("admin:stages_student_change", args=(student.pk,)))
    pdf = ExpertEdeLetterPdf(student)
    pdf.produce()

    with open(pdf.filename, mode='rb') as fh:
        response = HttpResponse(fh.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(os.path.basename(pdf.filename))
    return response


def print_mentor_ede_compensation_form(request, pk):
    """
    Imprime le PDF à envoyer au mentor EDE pour le mentoring
    """
    student = Student.objects.get(pk=pk)
    if not student.mentor:
        messages.error(request, "Aucun mentor n'est attribué à cet étudiant")
        return redirect(reverse("admin:stages_student_change", args=(student.pk,)))
    pdf = MentorCompensationPdfForm(student)
    pdf.produce()

    with open(pdf.filename, mode='rb') as fh:
        response = HttpResponse(fh.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(os.path.basename(pdf.filename))
    return response


class PrintKlassList(ZippedFilesBaseView):
    filename = 'archive_RolesDeClasses.zip'

    def generate_files(self):
        for klass in Klass.active.order_by('section', 'name'):
            pdf = KlassListPDF(klass)
            pdf.produce(klass)
            yield pdf.filename


class PrintChargeSheet(ZippedFilesBaseView):
    """
    Génère un pdf pour chaque enseignant, écrit le fichier créé
    dans une archive et renvoie une archive de pdf
    """
    filename = 'archive_FeuillesDeCharges.zip'

    def generate_files(self):
        queryset = Teacher.objects.filter(pk__in=self.request.GET.get('ids').split(','))
        for teacher in queryset:
            activities = teacher.calc_activity()
            pdf = ChargeSheetPDF(teacher)
            pdf.produce(activities)
            yield pdf.filename
