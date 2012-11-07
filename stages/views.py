# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, TemplateView

from .forms import PeriodForm
from .models import Section, Student, Corporation, Period, Training


class StudentSummaryView(DetailView):
    model = Student
    template_name = 'student_summary.html'


class CorporationSummaryView(DetailView):
    model = Corporation
    template_name = 'corporation_summary.html'


class AttributionView(TemplateView):
    template_name = 'attribution.html'

    def get_context_data(self, **kwargs):
        context = super(AttributionView, self).get_context_data(**kwargs)
        context.update({
            #'period_form': PeriodForm(),
            'sections': Section.objects.all(),
        })
        return context

# AJAX views:

def section_periods(request, pk):
    """ Return all periods from a section (JSON) """
    section = get_object_or_404(Section, pk=pk)
    periods = [(p.id, p.dates) for p in section.period_set.all()]
    return HttpResponse(json.dumps(periods), content_type="application/json")

def period_students(request, pk):
    """ Return all students from period's section, with corresponding Training
    if existing (JSON)
    """
    period = get_object_or_404(Period, pk=pk)
    students = period.section.student_set.all().order_by('last_name')
    trainings = dict((t.student_id, t.id) for t in Training.objects.filter(period=period))
    data = [{'name': unicode(s), 'id': s.id, 'training_id': trainings.get(s.id)} for s in students]
    return HttpResponse(json.dumps(data), content_type="application/json")

def period_corporations(request, pk):
    """ Return all corporations with availabilities in the specified period """
    period = get_object_or_404(Period, pk=pk)
    corps = [(av.corporation.id, av.corporation.name)
             for av in period.availability_set.select_related('corporation').all()]
    return HttpResponse(json.dumps(corps), content_type="application/json")

@csrf_exempt
def new_training(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    training = Training.objects.create(
        period=Period.objects.get(pk=request.POST.get('period')),
        student=Student.objects.get(pk=request.POST.get('student')),
        corporation=Corporation.objects.get(pk=request.POST.get('corp'))
    )
    return HttpResponse('OK')


def stages_export(request):
    from datetime import date
    from openpyxl import Workbook
    from openpyxl.writer.excel import save_virtual_workbook

    export_fields = [
        ('Prénom', 'student__first_name'), ('Nom', 'student__last_name'),
        ('Filière', 'period__section__name'),
        ('Début', 'period__start_date'), ('Fin', 'period__end_date'),
        ('Institution', 'corporation__name'),
        ('Domaine', 'domain__name'),
        ('Prénom référent', 'referent__first_name'), ('Nom référent', 'referent__last_name')
    ]

    wb = Workbook()
    ws = wb.get_active_sheet()
    ws.title = 'Stages'
    # Headers
    for col_idx, header in enumerate([f[0] for f in export_fields]):
        ws.cell(row=0, column=col_idx).value = header
        ws.cell(row=0, column=col_idx).style.font.bold = True
    # Data
    for row_idx, tr in enumerate(Training.objects.all().values_list(*[f[1] for f in export_fields]), start=1):
        for col_idx, field in enumerate(tr):
            ws.cell(row=row_idx, column=col_idx).value = field

    response = HttpResponse(save_virtual_workbook(wb), mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s%s.xlsx' % (
          'stages_export_', date.strftime(date.today(), '%Y-%m-%d'))
    return response
