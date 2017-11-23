from collections import OrderedDict

from django import forms
from django.contrib import admin
from django.db.models import BooleanField
from datetime import date
from stages.exports import OpenXMLExport
from .models import Candidate, GENDER_CHOICES


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
        if not cand.canceled_file:
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
    for candidate in queryset:
        if candidate.deposite_date is not None \
                and candidate.date_confirmation_mail is None \
                and candidate.canceled_file is False:
            # Send confirmation message
            src = request.user.email
            to = '{0}'.format(candidate.email)
            if candidate.corporation:
                to += ';'.format(candidate.corporation.email)
            if candidate.instructor:
                to += ';'.format(candidate.instructor.email)
            subject = "Confirmation de votre inscription à l'Ecole Santé-social Pierre-Coullery"
            msg = """
            Madame, Monsieur,<br><br>
            Nous vous confirmons la bonne réception de l'inscription de {0} {1} {2}
            dans la filière {3} pour l'année scolaire à venir.
            <br><br>
            Nous nous tenons à votre disposition pour tout renseignement complémentaire et 
            vous prions de recevoir, Madame, Monsieur, nos salutations les plus cordiales.<br><br>
            Secrétariat de l'EPC<br><br>
            tél. 032 886 33 00<br><br>
            {4} {5} <br><br>
            {6}
            """.format(candidate.civility, candidate.first_name, candidate.last_name, candidate.section,
                       request.user.first_name, request.user.last_name, request.user.email)
            print(src)
            print(subject)
            print(msg)
            print([to])

            """  ********************** to be uncommented  !!
            send_mail(
                subject,
                msg,
                src,
                [to],
                fail_silently=False,
            )
            **************************************************
            """

            candidate.date_confirmation_mail = date.today()
            candidate.save()
    return

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
    list_display = ('last_name', 'first_name', 'section', 'confirm_mail')
    list_filter = ('section', 'option')
    readonly_fields = ('total_result_points', 'total_result_mark', 'date_confirmation_mail')
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
                       ('interview_date', 'interview_room'),
                       ('examination_result', 'interview_result', 'file_result', 'total_result_points',
                        'total_result_mark')
                       ),
        }),
    )

    def confirm_mail(self, obj):
        return obj.date_confirmation_mail is not None
    confirm_mail.boolean = True

admin.site.register(Candidate, CandidateAdmin)
