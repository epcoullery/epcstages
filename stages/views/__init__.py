import io
import json
import os

from collections import OrderedDict
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import EmailMessage
from django.db.models import Count
from django.http import FileResponse, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateformat import format as django_format
from django.utils.text import slugify
from django.views.generic import DetailView, FormView, ListView, TemplateView, UpdateView

from .base import EmailConfirmationBaseView, PDFBaseView, ZippedFilesBaseView
from .export import OpenXMLExport
from .imports import HPContactsImportView, HPImportView, ImportReportsView, StudentImportView
from ..forms import CorporationMergeForm, EmailBaseForm, StudentCommentForm
from ..models import (
    Klass, Section, Student, Teacher, Corporation, CorpContact, Period,
    Training, Availability
)
from ..pdf import (
    ChargeSheetPDF, ExpertEdeLetterPdf, ExpertEdsLetterPdf, UpdateDataFormPDF,
    MentorCompensationPdfForm, KlassListPDF,
)
from ..utils import school_year_start


class CorporationListView(ListView):
    model = Corporation
    template_name = 'corporations.html'


class CorporationView(DetailView):
    model = Corporation
    template_name = 'corporation.html'
    context_object_name = 'corp'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class CorporationMergeView(FormView):
    form_class = CorporationMergeForm
    template_name = 'corporation_merge.html'
    success_url = reverse_lazy('corporations')

    def form_valid(self, form):
        if form.data['step'] != '2':
            return self.render_to_response(self.get_context_data(form=form))
        form.merge_corps()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step'] = '1'
        if context['form'].is_bound and context['form'].is_valid():
            context['step'] = '2'
            context['contacts_from'] = context['form'].cleaned_data['corp_merge_from'].corpcontact_set.all()
            context['contacts_to'] = context['form'].cleaned_data['corp_merge_to'].corpcontact_set.all()
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
        context.update({
            'students': self.object.student_set.filter(archived=False
                ).prefetch_related('training_set').order_by('last_name', 'first_name'),
            'show_option_ase': self.object.section.name.endswith('ASE'),
            'show_pp': self.object.section.has_stages,
            'show_employeur': not self.object.section.is_ESTER,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') != 'xls':
            return super().render_to_response(context, **response_kwargs)

        export = OpenXMLExport(self.object.name)
        headers = ['Nom', 'Prénom', 'Domicile', 'Date de naissance']
        col_widths = [18, 15, 20, 14]
        if context['show_option_ase']:
            headers.append('Orientation')
            col_widths.append(20)
        if context['show_employeur']:
            headers.append('Employeur')
            col_widths.append(24)
        if context['show_pp']:
            headers.extend(['Stage 1', 'Domaine 1', 'Stage 2', 'Domaine 2', 'Stage 3', 'Domaine 3'])
            col_widths.extend([25, 12, 25, 12, 25, 12])
        export.write_line(headers, bold=True, col_widths=col_widths)
        # Data
        for student in context['students']:
            values = [
                student.last_name, student.first_name,
                " ".join([student.pcode, student.city]), student.birth_date,
            ]
            if context['show_option_ase']:
                values.append(str(student.option_ase))
            if context['show_employeur']:
                values.append(
                    ", ".join([student.corporation.name, student.corporation.city])
                    if student.corporation else ''
                )
            if context['show_pp']:
                for training in student.training_set.select_related(
                            'availability', 'availability__corporation', 'availability__domain'
                        ).all():
                    values.append(training.availability.corporation.name)
                    values.append(training.availability.domain.name)
            export.write_line(values)

        return export.get_http_response('%s_export' % self.object.name.replace(' ', '_'))


class StudentCommentView(UpdateView):
    template_name = 'student_comment.html'
    model = Student
    form_class = StudentCommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only authorized teachers can comment on the student.
        if not self.object.can_comment(self.request.user):
            del context['form']
        return context

    def get_success_url(self):
        messages.success(
            self.request, "L'enregistrement des commentaires pour %s a réussi." % self.object
        )
        return reverse('class', args=[self.object.klass.pk])


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
    permission_required = 'stages.change_training'
    template_name = 'attribution.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
            'sections': Section.objects.filter(has_stages=True),
            'referents': referents,
        })
        return context


class StudentSummaryView(DetailView):
    model = Student
    template_name = 'student_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    return_fields = ['id', 'first_name', 'last_name', 'role', 'is_main', 'corporation_id']

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
    email_template = 'email/student_convocation_EDE.txt'

    @property
    def expert(self):
        return self.student.expert

    @property
    def internal_expert(self):
        return self.student.internal_expert

    @property
    def date_soutenance_mailed(self):
        return self.student.date_soutenance_mailed

    def missing_examination_data(self):
        return self.student.missing_examination_data()

    def dispatch(self, request, *args, **kwargs):
        self.student = Student.objects.get(pk=self.kwargs['pk'])
        errors = self.missing_examination_data()
        errors.extend(self.check_errors())
        if errors:
            messages.error(request, "\n".join(errors))
            return redirect(reverse("admin:stages_student_change", args=(self.student.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def check_errors(self):
        errors = []
        if not self.student.email:
            errors.append("L’étudiant-e n’a pas de courriel valide !")
        if self.expert and not self.expert.email:
            errors.append("L’expert externe n’a pas de courriel valide !")
        if self.internal_expert and not self.internal_expert.email:
            errors.append("L’expert interne n'a pas de courriel valide !")
        if self.date_soutenance_mailed is not None:
            errors.append("Une convocation a déjà été envoyée !")
        return errors

    def msg_context(self):
        # Recipients with ladies first!
        recip_names = sorted([
            self.student.civility_full_name,
            self.expert.civility_full_name,
            self.internal_expert.civility_full_name,
        ])
        titles = [
            self.student.civility,
            self.expert.civility,
            self.internal_expert.civility,
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
        return {
            'recipient1': recip_names[0],
            'recipient2': recip_names[1],
            'recipient3': recip_names[2],
            'student': self.student,
            'sender': self.request.user,
            'global_civilities': civilities,
            'date_examen': django_format(self.student.date_exam, 'l j F Y à H\hi') if self.student.date_exam else '-',
            'salle': self.student.room,
        }

    def get_initial(self):
        initial = super().get_initial()
        to = [self.student.email, self.expert.email, self.internal_expert.email]

        initial.update({
            'cci': self.request.user.email,
            'to': '; '.join(to),
            'subject': self.title,
            'message': loader.render_to_string(self.email_template, self.msg_context()),
            'sender': self.request.user.email,
        })
        return initial

    def on_success(self, student):
        self.student.date_soutenance_mailed = timezone.now()
        self.student.save()


class StudentConvocationEDSView(StudentConvocationExaminationView):
    title = "Convocation à la soutenance du travail final"
    email_template = 'email/student_convocation_EDS.txt'


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
            buff = io.BytesIO()
            pdf = UpdateDataFormPDF(buff, self.return_date)
            pdf.produce(klass)
            yield ('{0}.pdf'.format(klass.name), buff.getvalue())


class PrintExpertEDECompensationForm(PDFBaseView):
    """
    Imprime le PDF à envoyer à l'expert EDE en accompagnement du
    travail de diplôme
    """
    pdf_class = ExpertEdeLetterPdf

    def filename(self, student):
        return slugify('{0}_{1}'.format(student.last_name, student.first_name)) + '_Expert.pdf'

    def get_object(self):
        return Student.objects.get(pk=self.kwargs['pk'])

    def check_object(self, student):
        missing = student.missing_examination_data()
        if missing:
            messages.error(self.request, "\n".join(
                ["Toutes les informations ne sont pas disponibles pour la lettre à l’expert!"]
                + missing
            ))
            return redirect(reverse("admin:stages_student_change", args=(student.pk,)))

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        response = self.check_object(student)
        if response:
            return response
        return super().get(request, *args, **kwargs)


class PrintMentorEDECompensationForm(PDFBaseView):
    """
    Imprime le PDF à envoyer au mentor EDE pour le mentoring
    """
    pdf_class = MentorCompensationPdfForm

    def filename(self, student):
        return slugify(
            '{0}_{1}'.format(student.last_name, student.first_name)
        ) + '_Indemn_mentor.pdf'

    def get_object(self):
        return Student.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        if not student.mentor:
            messages.error(request, "Aucun mentor n'est attribué à cet étudiant")
            return redirect(reverse("admin:stages_student_change", args=(student.pk,)))
        return super().get(request, *args, **kwargs)


class PrintExpertEDSCompensationForm(PrintExpertEDECompensationForm):
    """
    Imprime le PDF à envoyer à l'expert EDS en accompagnement du
    travail final.
    """
    pdf_class = ExpertEdsLetterPdf

    def check_object(self, student):
        missing = student.missing_examination_data()
        if missing:
            messages.error(self.request, "\n".join(
                ["Toutes les informations ne sont pas disponibles pour la lettre à l’expert!"]
                + missing
            ))
            return redirect(reverse("admin:stages_student_change", args=(student.pk,)))


class PrintKlassList(ZippedFilesBaseView):
    filename = 'archive_RolesDeClasses.zip'

    def generate_files(self):
        for klass in Klass.active.order_by('section', 'name'):
            buff = io.BytesIO()
            pdf = KlassListPDF(buff, klass)
            pdf.produce(klass)
            filename = slugify(klass.name + '.pdf')
            yield (filename, buff.getvalue())


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
            buff = io.BytesIO()
            pdf = ChargeSheetPDF(buff, teacher)
            pdf.produce(activities)
            filename = slugify('{0}_{1}'.format(teacher.last_name, teacher.first_name)) + '.pdf'
            yield (filename, buff.getvalue())
