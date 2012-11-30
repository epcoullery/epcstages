# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView, ListView

from .forms import PeriodForm
from .models import Section, Student, Corporation, Period, Training, Referent, Availability


class StudentSummaryView(DetailView):
    model = Student
    template_name = 'student_summary.html'


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
        context.update({
            #'period_form': PeriodForm(),
            'sections': Section.objects.all(),
            'referents': Referent.objects.all().order_by('last_name', 'first_name'),
        })
        return context

# AJAX views:

def section_periods(request, pk):
    """ Return all periods from a section (JSON) """
    section = get_object_or_404(Section, pk=pk)
    periods = [(p.id, p.dates) for p in section.period_set.all()]
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
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    training = get_object_or_404(Training, pk=request.POST.get('pk'))
    training.delete()
    return HttpResponse('OK')


def stages_export(request):
    from datetime import date
    from openpyxl import Workbook
    from openpyxl.writer.excel import save_virtual_workbook

    export_fields = [
        ('Prénom', 'student__first_name'), ('Nom', 'student__last_name'),
        ('Classe', 'student__klass__name'), ('Filière', 'student__klass__section__name'),
        ('Début', 'availability__period__start_date'), ('Fin', 'availability__period__end_date'),
        ('Institution', 'availability__corporation__name'),
        ('Domaine', 'availability__domain__name'),
        ('Prénom référent', 'referent__first_name'), ('Nom référent', 'referent__last_name')
    ]

    period_filter = request.GET.get('filter')
    if period_filter:
        query = Training.objects.filter(availability__period_id=period_filter)
    else:
        query = Training.objects.all()

    wb = Workbook()
    ws = wb.get_active_sheet()
    ws.title = 'Stages'
    # Headers
    for col_idx, header in enumerate([f[0] for f in export_fields]):
        ws.cell(row=0, column=col_idx).value = header
        ws.cell(row=0, column=col_idx).style.font.bold = True
    # Data
    for row_idx, tr in enumerate(query.values_list(*[f[1] for f in export_fields]), start=1):
        for col_idx, field in enumerate(tr):
            ws.cell(row=row_idx, column=col_idx).value = field

    response = HttpResponse(save_virtual_workbook(wb), mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s%s.xlsx' % (
          'stages_export_', date.strftime(date.today(), '%Y-%m-%d'))
    return response
