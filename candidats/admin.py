from collections import OrderedDict

from django.contrib import admin
from django.db.models import BooleanField
from django.urls import reverse
from django.utils.html import format_html

from stages.exports import OpenXMLExport
from .forms import CandidateForm
from .models import Candidate, Interview, GENDER_CHOICES


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
    form = CandidateForm
    list_display = ('last_name', 'first_name', 'section', 'confirm_mail', 'validation_mail', 'convocation_mail')
    list_filter = ('section', 'option')
    search_fields = ('last_name', 'city')
    readonly_fields = (
        'total_result_points', 'total_result_mark', 'confirmation_date',
        'convocation_date', 'candidate_actions',
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
                        ('interview',),
                        ('examination_result', 'interview_result', 'file_result', 'total_result_points',
                            'total_result_mark'),
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

    def validation_mail(self, obj):
        return obj.validation_date is not None
    validation_mail.boolean = True

    def convocation_mail(self, obj):
        return obj.convocation_date is not None
    convocation_mail.boolean = True

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


class InterviewAdmin(admin.ModelAdmin):
    pass


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Interview, InterviewAdmin)
