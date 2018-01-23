from collections import OrderedDict
from datetime import date
from django import forms

from django.contrib import admin
from django.core.mail import EmailMessage
from django.db.models import BooleanField, Q
from django.template import loader

from stages.exports import OpenXMLExport
from .models import Candidate, GENDER_CHOICES, Interview


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


def send_confirmation_mail(modeladmin, request, queryset):
    from_email = request.user.email
    subject = "Confirmation de votre inscription à l'Ecole Santé-social Pierre-Coullery"
    email_sent = 0

    for candidate in queryset.filter(
            deposite_date__isnull=False, date_confirmation_mail__isnull=True, canceled_file=False):
        to = [candidate.email]

        if candidate.corporation and candidate.corporation.email:
            to.append(candidate.corporation.email)
        if candidate.instructor and candidate.instructor.email:
            to.append(candidate.instructor.email)

        context = {
            'candidate_civility': candidate.civility,
            'candidate_name': " ".join([candidate.civility, candidate.first_name, candidate.last_name]),
            'section': candidate.section,
            'sender_name': " ".join([request.user.first_name, request.user.last_name]),
            'sender_email': from_email,
        }

        if candidate.section == 'EDE':
            body = loader.render_to_string('email/candidate_confirm_EDE.txt', context)
        else:
            body = loader.render_to_string('email/candidate_confirm_FE.txt', context)

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email= request.user.email,
            to=to,
            bcc=[request.user.email]
        )

        try:
            email.send()
            email_sent += 1
            candidate.date_confirmation_mail = date.today()
            candidate.save()
        except Exception as err:
            modeladmin.message_user(request, "Échec d’envoi pour le candidat {0} ({1})".format(candidate, err))
        modeladmin.message_user(request, "%d messages de confirmation ont été envoyés." % email_sent)

send_confirmation_mail.short_description = "Envoyer email de confirmation"


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
    list_display = ('last_name', 'first_name', 'section', 'option', 'confirm_mail', 'send_convocation')
    list_filter = ('section', 'option')
    readonly_fields = ('total_result_points', 'total_result_mark', 'date_confirmation_mail', 'convocation_sended_email')
    actions = [export_candidates, send_confirmation_mail]
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name', 'gender'),
                       ('street', 'pcode', 'city', 'district'),
                       ('mobile', 'email'),
                       ('birth_date', 'avs', 'handicap', 'has_photo'),
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
                       ('interview'),
                       ('examination_result', 'interview_result', 'file_result', 'total_result_points',
                        'total_result_mark')
                       ),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.interview is None:
            obj.convocation_sended_email = None
        return super().save_model(request, obj, form, change)

    def send_convocation(self, obj):
        if obj.section == 'EDE':
            if not obj.convocation_sended_email:
                if obj.interview:
                    return "<a href=\"/admin/{0}/convocation\">Envoyer convocation</a>".format(obj.id)
                else:
                    return 'en attente'
            else:
                return obj.interview
        else:
            return '---'

    send_convocation.short_description = "Entretien d'admission"
    send_convocation.allow_tags = True

    def confirm_mail(self, obj):
        return obj.date_confirmation_mail is not None
    confirm_mail.boolean = True


def send_interviews_schedule(modeladmin, request, queryset):
    """
    Send schedule of interviews to teachers
    """
    teachers_concerned = []
    for interview in Interview.objects.all():
        if not interview.teacher_1 in teachers_concerned:
            teachers_concerned.append(interview.teacher_1)
        if not interview.teacher_2 in teachers_concerned:
            teachers_concerned.append(interview.teacher_2)

    for prof in teachers_concerned:
        interviews = Interview.objects.filter(Q(teacher_1=prof) |
                                              Q(teacher_2=prof))
send_interviews_schedule.short_description = 'Email aux enseignants'


class InterviewAdmin(admin.ModelAdmin):
    actions = (send_interviews_schedule,)


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Interview, InterviewAdmin)