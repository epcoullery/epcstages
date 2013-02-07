# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import date

from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
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
            ).filter(availability__period__pk=self.kwargs['pk'])


class AttributionView(TemplateView):
    template_name = 'attribution.html'

    def get_context_data(self, **kwargs):
        context = super(AttributionView, self).get_context_data(**kwargs)
        # Need 2 queries, because referents with no training item would not appear in the second query
        referents = Referent.objects.all().order_by('last_name', 'first_name')
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

# AJAX views:

def section_periods(request, pk):
    """ Return all periods from a section (JSON) """
    section = get_object_or_404(Section, pk=pk)
    periods = [{'id': p.id, 'dates': p.dates, 'title': p.title}
               for p in section.period_set.all().order_by('-start_date')]
    return HttpResponse(json.dumps(periods), content_type="application/json")

def section_classes(request, pk):
    section = get_object_or_404(Section, pk=pk)
    classes = [(k.id, k.name) for k in section.klass_set.all()]
    return HttpResponse(json.dumps(classes), content_type="application/json")


def period_students(request, pk):
    """
    Return all students from period's section and level,
    with corresponding Training if existing (JSON)
    """
    period = get_object_or_404(Period, pk=pk)
    students = Student.objects.filter(klass__section=period.section, klass__level=period.level).order_by('last_name')
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
    corps = [{'id': av.id, 'corp_name': av.corporation.name, 'domain': av.domain.name, 'free': av.free}
             for av in period.availability_set.select_related('corporation').all()]
    return HttpResponse(json.dumps(corps), content_type="application/json")

def new_training(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    ref_key = request.POST.get('referent')
    try:
        ref = Referent.objects.get(pk=ref_key) if ref_key else None
        training = Training.objects.create(
            student=Student.objects.get(pk=request.POST.get('student')),
            availability=Availability.objects.get(pk=request.POST.get('avail')),
            referent=ref,
        )
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


def stages_export(request):
    from datetime import date
    from openpyxl import Workbook
    from openpyxl.writer.excel import save_virtual_workbook

    export_fields = [
        ('Prénom', 'student__first_name'), ('Nom', 'student__last_name'),
        ('Classe', 'student__klass__name'), ('Filière', 'student__klass__section__name'),
        ('Début', 'availability__period__start_date'), ('Fin', 'availability__period__end_date'),
        ('Prénom référent', 'referent__first_name'), ('Nom référent', 'referent__last_name'),
        ('Institution', 'availability__corporation__name'),
        ('Rue Inst.', 'availability__corporation__street'),
        ('NPA Inst.', 'availability__corporation__pcode'),
        ('Ville Inst.', 'availability__corporation__city'),
        ('Domaine', 'availability__domain__name'),
        ('Civilité contact', None), ('Prénom contact', None), ('Nom contact', None),
    ]

    period_filter = request.GET.get('filter')
    if period_filter:
        query = Training.objects.filter(availability__period_id=period_filter)
    else:
        query = Training.objects.all()

    contacts = {}
    for contact in CorpContact.objects.all().select_related('corporation').order_by('corporation'):
        if contact.corporation.name not in contacts or contact.is_main is True:
            contacts[contact.corporation.name] = contact

    wb = Workbook()
    ws = wb.get_active_sheet()
    ws.title = 'Stages'
    # Headers
    for col_idx, header in enumerate([f[0] for f in export_fields]):
        ws.cell(row=0, column=col_idx).value = header
        ws.cell(row=0, column=col_idx).style.font.bold = True
    # Data
    query_keys = [f[1] for f in export_fields if f[1] is not None]
    for row_idx, tr in enumerate(query.values(*query_keys), start=1):
        for col_idx, field in enumerate(query_keys):
            ws.cell(row=row_idx, column=col_idx).value = tr[field]
        contact = contacts.get(tr['availability__corporation__name'])
        if contact:
            ws.cell(row=row_idx, column=col_idx+1).value = contact.title
            ws.cell(row=row_idx, column=col_idx+2).value = contact.first_name
            ws.cell(row=row_idx, column=col_idx+3).value = contact.last_name

    response = HttpResponse(save_virtual_workbook(wb), mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s%s.xlsx' % (
          'stages_export_', date.strftime(date.today(), '%Y-%m-%d'))
    return response
