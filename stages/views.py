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
