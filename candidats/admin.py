from collections import OrderedDict

from django.contrib import admin
from django.db.models import BooleanField
from django.urls import reverse
from django.utils.html import format_html

from stages.exports import OpenXMLExport
from .forms import CandidateForm
from .models import (Candidate, Interview, GENDER_CHOICES, DIPLOMA_CHOICES, DIPLOMA_STATUS_CHOICES,
                     SECTION_CHOICES, OPTION_CHOICES, AES_ACCORDS_CHOICES, RESIDENCE_PERMITS_CHOICES)


def export_candidates(modeladmin, request, queryset):
    """
    Export all candidates fields.
    """
    export_fields = OrderedDict([
        (getattr(f, 'verbose_name', f.name), f.name)
        for f in Candidate._meta.get_fields() if f.name != 'ID'
    ])
    boolean_fields = [f.name for f in Candidate._meta.get_fields() if isinstance(f, BooleanField)]
    export_fields['Employeur'] = 'corporation__name'
    export_fields['FEE/FPP'] = 'instructor__last_name'
    export_fields['Prof. entretien'] = 'interview__teacher_int__abrev'
    export_fields['Correct. dossier'] = 'examination_teacher__abrev'
    export_fields['Prof. dossier'] = 'interview__teacher_file__abrev'
    export_fields['Date entretien'] = 'interview__date'
    export_fields['Salle entretien'] = 'interview__room'
    del export_fields['interview']


    export = OpenXMLExport('Exportation')
    export.write_line(export_fields.keys(), bold=True)
    for cand in queryset.values_list(*export_fields.values()):
        values = []
        for value, field_name in zip(cand, export_fields.values()):
            if field_name == 'gender':
                value = dict(GENDER_CHOICES)[value]
            if field_name == 'section':
                value = dict(SECTION_CHOICES)[value]
            if field_name == 'option':
                value = dict(OPTION_CHOICES)[value]
            if field_name == 'diploma':
                value = dict(DIPLOMA_CHOICES)[value]
            if field_name == 'diploma_status':
                value = dict(DIPLOMA_STATUS_CHOICES)[value]
            if field_name == 'aes_accords':
                value = dict(AES_ACCORDS_CHOICES)[value]
            if field_name == 'residence_permits':
                value = dict(RESIDENCE_PERMITS_CHOICES)[value]
            if field_name in boolean_fields:
                value = 'Oui' if value else ''
            values.append(value)
        export.write_line(values)
    return export.get_http_response('candidats_export')

export_candidates.short_description = "Exporter les candidats sélectionnés"


class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm
    list_display = ('last_name', 'first_name', 'section', 'confirm_mail', 'convocation')
    list_filter = ('section', 'option')
    readonly_fields = (
        'total_result_points', 'total_result_mark', 'confirmation_date', 'validation_date',
        'convocation_date', 'candidate_actions', 'total_result',
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
                       ('deposite_date', 'confirmation_date', 'canceled_file'),
                       'comment',
                      ),
        }),
        ("FE", {
            'classes': ('collapse',),
            'fields': (('exemption_ecg', 'integration_second_year', 'validation_sfpo'),),
        }),
        ("EDE/EDS", {
            'classes': ('collapse',),
            'fields': (('diploma', 'diploma_detail', 'diploma_status'),
                        ('registration_form', 'has_photo', 'certificate_of_payement', 'cv', 'police_record', 'reflexive_text',
                        'marks_certificate', 'residence_permits', 'aes_accords'),
                        ('certif_of_800_childhood', 'certif_of_800_general', 'work_certificate'),
                        ('promise', 'contract', 'activity_rate'),
                        ('inscr_other_school',),
                        ('interview', 'examination_teacher'),
                        ('examination_result', 'interview_result', 'file_result', 'total_result',),
                        ('confirmation_date', 'validation_date', 'convocation_date'),
            ),
        }),
        (None, {
            'fields': (('candidate_actions',)),
        }),
    )

    def confirm_mail(self, obj):
        return obj.confirmation_date is not None
    confirm_mail.boolean = True

    def convocation(self, obj):
        if obj.interview is None:
            return '???'
        elif obj.interview and obj.convocation_date:
            return obj.interview
        else:
            url = reverse('candidate-convocation', args=[obj.pk])
            return format_html('<a href="' + url  + '">Envoyer convocation</a>')
    convocation.short_description = 'Convoc. aux examens'
    convocation.allow_tags = True

    def candidate_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Confirmation de réception</a>&nbsp;'
            '<a class="button" href="{}">Validation enseignants EDE</a>&nbsp;'
            '<a class="button" href="{}">Convocation aux examens EDE</a>&nbsp;'
            '<a class="button" href="{}">Impression du résumé du dossier EDE</a>',
            reverse('candidate-confirmation', args=[obj.pk]),
            reverse('candidate-validation', args=[obj.pk]),
            reverse('candidate-convocation', args=[obj.pk]),
            reverse('candidate-summary', args=[obj.pk]),
        )
    candidate_actions.short_description = 'Actions pour candidats'
    candidate_actions.allow_tags = True

    def total_result(self, obj):
        if obj.examination_result is None:
            obj.examination_result = 0
        if obj.interview_result is None:
            obj.interview_result = 0
        if obj.file_result is None:
            obj.file_result = 0
        tot =  obj.examination_result + obj.interview_result + obj.file_result
        obj.tot_result_points = tot
        return tot
    total_result.short_description = 'Total des points'



class InterviewAdmin(admin.ModelAdmin):
    pass


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Interview, InterviewAdmin)
