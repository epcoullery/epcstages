# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import date, datetime, timedelta

from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict
from django.views.generic import DetailView, TemplateView, ListView

from .forms import PeriodForm
from .models import (Section, Student, Corporation, CorpContact, Period,
    Training, Referent, Availability)


def school_year_start():
    """ Return first official day of current school year """
    current_year = date.today().year
    if date(current_year, 8, 1) > date.today():
        return date(current_year-1, 8, 1)
    else:
        return date(current_year, 8, 1)


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
        school_years = SortedDict()
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
        referents = Referent.objects.all().order_by('last_name', 'first_name')

        # Populate each referent with the number of referencies done during the current school year
        ref_counts = dict([(ref.id, ref.num_refs)
                for ref in Referent.objects.filter(training__availability__period__end_date__gte=school_year_start
                ).annotate(num_refs=Count('training'))])
        for ref in referents:
            ref.num_refs = ref_counts.get(ref.id, 0)

        context.update({
            #'period_form': PeriodForm(),
            'sections': Section.objects.all(),
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
        return CorpContact.objects.filter(corporation__pk=self.kwargs['pk'])

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
        'name': unicode(s),
        'id': s.id,
        'training_id': trainings.get(s.id),
        'klass': s.klass.name} for s in students]
    return HttpResponse(json.dumps(data), content_type="application/json")

def period_availabilities(request, pk):
    """ Return all availabilities in the specified period """
    period = get_object_or_404(Period, pk=pk)
    corps = [{'id': av.id, 'id_corp': av.corporation.id, 'corp_name': av.corporation.name,
              'domain': av.domain.name, 'free': av.free}
             for av in period.availability_set.select_related('corporation').all()]
    return HttpResponse(json.dumps(corps), content_type="application/json")

def new_training(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    ref_key = request.POST.get('referent')
    cont_key = request.POST.get('contact')
    try:
        ref = Referent.objects.get(pk=ref_key) if ref_key else None
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
    return HttpResponse('OK')

def del_training(request):
    """ Delete training and return the referent id """
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    training = get_object_or_404(Training, pk=request.POST.get('pk'))
    ref_id = training.referent_id
    training.delete()
    return HttpResponse(json.dumps({'ref_id': ref_id}), content_type="application/json")


EXPORT_FIELDS = [
    ('Prénom', 'student__first_name'), ('Nom', 'student__last_name'),
    ('ID externe', 'student__ext_id'),
    ('Classe', 'student__klass__name'), ('Filière', 'student__klass__section__name'),
    ('Nom du stage', 'availability__period__title'),
    ('Début', 'availability__period__start_date'), ('Fin', 'availability__period__end_date'),
    ('Remarques stage', 'comment'),
    ('Prénom référent', 'referent__first_name'), ('Nom référent', 'referent__last_name'),
    ('Courriel référent', 'referent__email'),
    ('Institution', 'availability__corporation__name'),
    ('ID externe Inst.', 'availability__corporation__ext_id'),
    ('Rue Inst.', 'availability__corporation__street'),
    ('NPA Inst.', 'availability__corporation__pcode'),
    ('Ville Inst.', 'availability__corporation__city'),
    ('Tél Inst.', 'availability__corporation__tel'),
    ('Domaine', 'availability__domain__name'),
    ('Remarques Inst.', 'availability__comment'),
    ('Civilité contact', 'availability__contact__title'),
    ('Prénom contact', 'availability__contact__first_name'),
    ('Nom contact', 'availability__contact__last_name'),
    ('ID externe contact', 'availability__contact__ext_id'),
    ('Tél contact', 'availability__contact__tel'),
    ('Courriel contact', 'availability__contact__email'),
    ('Courriel contact - copie', None),
]

NON_ATTR_EXPORT_FIELDS = [
    ('Filière', 'period__section__name'),
    ('Nom du stage', 'period__title'),
    ('Début', 'period__start_date'), ('Fin', 'period__end_date'),
    ('Institution', 'corporation__name'),
    ('Rue Inst.', 'corporation__street'),
    ('NPA Inst.', 'corporation__pcode'),
    ('Ville Inst.', 'corporation__city'),
    ('Tél Inst.', 'corporation__tel'),
    ('Domaine', 'domain__name'),
    ('Remarques Inst.', 'comment'),
    ('Civilité contact', 'contact__title'),
    ('Prénom contact', 'contact__first_name'),
    ('Nom contact', 'contact__last_name'),
    ('Tél contact', 'contact__tel'),
    ('Courriel contact', 'contact__email'),
    ('Courriel contact - copie', None),
]

def stages_export(request, scope=None):
    from datetime import date
    from openpyxl import Workbook
    from openpyxl.styles import Font, Style
    from openpyxl.writer.excel import save_virtual_workbook

    period_filter = request.GET.get('period')
    non_attributed = bool(int(request.GET.get('non_attr', 0)))

    export_fields = EXPORT_FIELDS
    contact_test_field = 'availability__contact__last_name'
    corp_name_field = 'availability__corporation__name'

    if period_filter:
        if non_attributed:
            # Export non attributed availabilities for a specific period
            query = Availability.objects.filter(period_id=period_filter, training__isnull=True)
            export_fields = NON_ATTR_EXPORT_FIELDS
            contact_test_field = 'contact__last_name'
            corp_name_field = 'corporation__name'
        else:
            # Export trainings for a specific period
            query = Training.objects.filter(availability__period_id=period_filter)
    else:
        if scope and scope == 'all':
            # Export all trainings in the database
            query = Training.objects.all()
        else:
            query = Training.objects.filter(availability__period__end_date__gt=school_year_start())

    # Prepare "default" contacts (when not defined on training)
    default_contacts = dict((c, '') for c in Corporation.objects.all().values_list('name', flat=True))
    always_ccs = dict((c, []) for c in Corporation.objects.all().values_list('name', flat=True))
    for contact in CorpContact.objects.all().select_related('corporation').order_by('corporation'):
        if not default_contacts[contact.corporation.name] or contact.is_main is True:
            default_contacts[contact.corporation.name] = contact
        if contact.always_cc:
            always_ccs[contact.corporation.name].append(contact)

    wb = Workbook()
    ws = wb.get_active_sheet()
    ws.title = 'Stages'
    bold = Style(font=Font(bold=True))
    # Headers
    for col_idx, header in enumerate([f[0] for f in export_fields], start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = header
        cell.style = bold
    # Data
    query_keys = [f[1] for f in export_fields if f[1] is not None]
    for row_idx, tr in enumerate(query.values(*query_keys), start=2):
        for col_idx, field in enumerate(query_keys, start=1):
            ws.cell(row=row_idx, column=col_idx).value = tr[field]
        if tr[contact_test_field] is None:
            # Use default contact
            contact = default_contacts.get(tr[corp_name_field])
            if contact:
                ws.cell(row=row_idx, column=col_idx-3).value = contact.title
                ws.cell(row=row_idx, column=col_idx-2).value = contact.first_name
                ws.cell(row=row_idx, column=col_idx-1).value = contact.last_name
                ws.cell(row=row_idx, column=col_idx).value = contact.email
        if always_ccs[tr[corp_name_field]]:
            ws.cell(row=row_idx, column=col_idx+1).value = "; ".join([c.email for c in always_ccs[tr[corp_name_field]]])

    response = HttpResponse(save_virtual_workbook(wb), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s%s.xlsx' % (
          'stages_export_', date.strftime(date.today(), '%Y-%m-%d'))
    return response
