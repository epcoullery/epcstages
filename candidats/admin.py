from collections import OrderedDict
from django.contrib import admin
from django.db.models import BooleanField
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect

from stages.exports import OpenXMLExport
from .models import Candidate, Interview, GENDER_CHOICES
from .forms import CandidateAdminForm


def export_candidates(modeladmin, request, queryset):
    """
    Export all candidates fields.
    """
    export_fields = OrderedDict(
        [(f.verbose_name, f.name) for f in Candidate._meta.get_fields() if f.name != 'ID']
    )
    boolean_fields = [f.name for f in Candidate._meta.get_fields() if isinstance(f, BooleanField)]
    export_fields['Employeur'] = 'corporation__name'
    export_fields['Employeur_localite'] = 'corporation__city'
    export_fields['FEE/FPP'] = 'instructor__last_name'

    export = OpenXMLExport('Exportation')
    export.write_line(export_fields.keys(), bold=True)
    for cand in queryset.values_list(*export_fields.values()):
        values = []
        for value, field_name in zip(cand, export_fields.values()):
            if field_name == 'gender':
                value = dict(GENDER_CHOICES)[value]
            if field_name in boolean_fields:
                value = 'Oui' if value else ''
            values.append(value)
        export.write_line(values)
    return export.get_http_response('candidats_export')

export_candidates.short_description = "Exporter les candidats sélectionnés"


class CandidateAdmin(admin.ModelAdmin):
    form = CandidateAdminForm
    list_display = ('last_name', 'first_name', 'section', 'confirm_mail', 'validation_mail', 'convocation')
    list_filter = ('section', 'option')
    readonly_fields = ('total_result_points', 'total_result_mark', 'date_confirmation_mail',
                       'date_validation_mail', 'date_convocation_mail'
                       )
    actions = [export_candidates]
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name', 'gender'),
                       ('street', 'pcode', 'city', 'district'),
                       ('mobile', 'email'),
                       ('birth_date', 'avs', 'handicap'),
                       ('section', 'option'),
                       ('corporation', 'instructor'),
                       ('deposite_date', 'date_confirmation_mail', 'canceled_file'),
                       'comment',
                       ),
        }),
        ("FE", {
            'classes': ('collapse',),
            'fields': (('exemption_ecg', 'integration_second_year', 'validation_sfpo'),),
        }),
        ("EDE/EDS", {
            'classes': ('collapse',),
            'fields': (
                        ('diploma', 'diploma_detail', 'diploma_status'),
                        ('registration_form', 'has_photo', 'certificate_of_payement', 'cv', 'police_record',
                         'reflexive_text', 'marks_certificate', 'residence_permits', 'aes_accords'),
                        ('certif_of_800_childhood', 'certif_of_800_general', 'work_certificate'),
                        ('promise', 'contract', 'activity_rate'),
                        ('interview',),
                        ('examination_result', 'interview_result', 'file_result', 'total_result_points',
                         'total_result_mark'),
                        ('date_confirmation_mail', 'date_validation_mail', 'date_convocation_mail'),
            ),
        }),
    )

    def response_change(self, request, obj):
        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        super(CandidateAdmin, self).response_change(request, obj)

        if "_confirmation" in request.POST:
            url = reverse('candidate-confirmation', kwargs={'pk': obj.id})
            return HttpResponseRedirect(url)
        elif "_validation" in request.POST:
            url = reverse('candidate-validation', kwargs={'pk': obj.id})
            return HttpResponseRedirect(url)
        elif "_convocation" in request.POST:
            url = reverse('candidate-convocation', kwargs={'pk': obj.id})
            return HttpResponseRedirect(url)
        elif "_summary" in request.POST:
            url = reverse('candidate-summary', kwargs={'pk': obj.id})
            return HttpResponseRedirect(url)
        return redirect('/admin/candidats/candidate/')

    def confirm_mail(self, obj):
        return obj.date_confirmation_mail is not None
    confirm_mail.boolean = True
    confirm_mail.short_description = "Mail de confirmation"

    def validation_mail(selfself, obj):
        return obj.date_validation_mail is not None
    validation_mail.boolean = True
    validation_mail.short_descritpion = "Valid. examen EDE"

    def convocation(self, obj):
        if obj.interview is None:
            return '???'
        elif obj.interview and obj.date_convocation_mail:
            return obj.interview
        else:
            url = reverse('candidate-convocation', args=[obj.pk])
            return '<a href="{0}">Envoyer convocation</a>'.format(url)
    convocation.short_description = 'Convoc. examens EDE'
    convocation.allow_tags = True


class InterviewAdmin(admin.ModelAdmin):
    pass


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Interview, InterviewAdmin)
