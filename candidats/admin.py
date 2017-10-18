from django import forms
from django.contrib import admin

from .models import Candidate


class CandidateAdminForm(forms.ModelForm):
    class Meta:
        model = Candidate
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 100, 'rows': 1}),
            'pcode': forms.TextInput(attrs={'size': 10}),
        }
        fields = '__all__'


class CandidateAdmin(admin.ModelAdmin):
    form = CandidateAdminForm
    list_display = ('last_name', 'first_name', 'section', 'confirm_email')
    list_filter = ('section', 'option')
    readonly_fields = ('total_result_points', 'total_result_mark', 'date_confirmation_mail')
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
            'fields': (('registration_form', 'certificate_of_payement', 'cv', 'certif_of_cfc',
                        'police_record', 'certif_of_800h', 'reflexive_text', 'work_certificate',
                        'marks_certificate', 'proc_admin_ext', 'promise', 'contract'),
                       'comment',
                       ('interview_date', 'interview_room'),
                       ('examination_result', 'interview_result', 'file_result', 'total_result_points',
                        'total_result_mark')
                       ),
        }),
    )

    def confirm_email(self, obj):
        return obj.date_confirmation_mail is not None
    confirm_email.boolean = True

admin.site.register(Candidate, CandidateAdmin)
