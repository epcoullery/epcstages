from collections import OrderedDict
from copy import deepcopy

from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.admin import GroupAdmin as AuthGroupAdmin
from django.contrib.auth.models import Group
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .models import (
    Teacher, Option, Student, StudentFile, Section, Level, Klass, Corporation,
    CorpContact, Domain, Period, Availability, Training, Course,
    LogBookReason, LogBook, ExamEDESession, Examination, SupervisionBill
)
from .views.export import OpenXMLExport


def print_charge_sheet(modeladmin, request, queryset):
    return HttpResponseRedirect(
        reverse('print-charge-sheet') + '?ids=%s' % ",".join(
            request.POST.getlist(ACTION_CHECKBOX_NAME)
        )
    )
print_charge_sheet.short_description = "Imprimer les feuilles de charge"


class ArchivedListFilter(admin.BooleanFieldListFilter):
    """
    Default filter that shows by default unarchived elements.
    """
    def __init__(self, request, params, *args, **kwargs):
        super().__init__(request, params, *args, **kwargs)
        if self.lookup_val is None:
            self.lookup_val = '0'

    def choices(self, cl):
        # Removing the "all" choice
        return list(super().choices(cl))[1:]

    def queryset(self, request, queryset):
        if not self.used_parameters:
            self.used_parameters[self.lookup_kwarg] = '0'
        return super().queryset(request, queryset)


class KlassRelatedListFilter(admin.RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        return [
            (k.pk, k.name) for k in Klass.active.order_by('name')
        ]


class StudentInline(admin.StackedInline):
    model = Student
    ordering = ('last_name', 'first_name')
    fields = (
        ('last_name', 'first_name', 'birth_date'),
        ('pcode', 'city', 'tel', 'mobile', 'email'),
    )
    can_delete = False
    extra = 0


class KlassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    ordering = ('name',)
    list_filter = ('section', 'level',)
    fields = (
        ('name',),
        ('section', 'level'),
        ('teacher', 'teacher_ecg', 'teacher_eps'),
    )
    inlines = [StudentInline]


class LogBookInline(admin.TabularInline):
    model = LogBook
    ordering = ('input_date',)
    fields = ('start_date', 'end_date', 'reason', 'comment', 'nb_period')
    extra = 0


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'abrev', 'email', 'contract', 'rate', 'total_logbook', 'archived')
    list_filter = (('archived', ArchivedListFilter), 'contract')
    search_fields = ('last_name', 'first_name', 'email')
    fields = (('civility', 'last_name', 'first_name', 'abrev'),
              ('birth_date', 'email', 'ext_id'),
              ('contract', 'rate', 'can_examinate', 'archived'),
              ('previous_report', 'next_report', 'total_logbook'),
              ('user'))
    readonly_fields = ('total_logbook',)
    actions = [print_charge_sheet]
    inlines = [LogBookInline]


class SupervisionBillInline(admin.TabularInline):
    model = SupervisionBill
    extra = 0


class ExaminationInline(admin.StackedInline):
    model = Examination
    extra = 1
    verbose_name = "Procédure de qualification"
    verbose_name_plural = "Procédures de qualification"
    autocomplete_fields = ('internal_expert', 'external_expert')
    fields = (('session', 'type_exam', 'date_exam', 'room'),
              ('internal_expert', 'external_expert'),
              ('mark', 'mark_acq'),
              ('examination_actions'),
              ('date_soutenance_mailed', 'date_confirm_received'),)
    readonly_fields = (
        'examination_actions', 'date_soutenance_mailed'
    )

    def examination_actions(self, obj):
        missing_message = mark_safe(
            '<div class="warning">Veuillez compléter les informations '
            'd’examen (date/salle/experts) pour accéder aux boutons d’impression.</div>'
        )
        if obj and obj.student.is_ede():
            if obj.missing_examination_data():
                return missing_message
            else:
                return format_html(
                    '<a class="button" href="{}">Courrier pour l’expert</a>&nbsp;'
                    '<a class="button" href="{}">Mail convocation soutenance</a>&nbsp;'
                    '<a class="button" href="{}">Indemnité EP</a>&nbsp;'
                    '<a class="button" href="{}">Indemnité soutenance</a>',
                    reverse('print-expert-letter-ede', args=[obj.pk]),
                    reverse('student-ede-convocation', args=[obj.pk]),
                    reverse('print-compens-form', args=[obj.pk, 'ep']),
                    reverse('print-compens-form', args=[obj.pk, 'sout']),
                )
        elif obj and obj.student.is_eds():
            if obj.missing_examination_data():
                return missing_message
            else:
                return format_html(
                    '<a class="button" href="{}">Courrier pour l’expert</a>&nbsp;'
                    '<a class="button" href="{}">Mail convocation soutenance</a>&nbsp;'
                    '<a class="button" href="{}">Indemnité EP</a>&nbsp;'
                    '<a class="button" href="{}">Indemnité soutenance</a>',
                    reverse('print-expert-letter-eds', args=[obj.pk]),
                    reverse('student-eds-convocation', args=[obj.pk]),
                    reverse('print-compens-form', args=[obj.pk, 'ep']),
                    reverse('print-compens-form', args=[obj.pk, 'sout']),
                )
        else:
            return missing_message
    examination_actions.short_description = 'Actions pour la procédure'


class StudentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'pcode', 'city', 'klass', 'archived')
    ordering = ('last_name', 'first_name')
    list_filter = (('archived', ArchivedListFilter), ('klass', KlassRelatedListFilter))
    search_fields = ('last_name', 'first_name', 'pcode', 'city', 'klass__name')
    autocomplete_fields = ('corporation', 'instructor', 'instructor2', 'supervisor', 'mentor')
    readonly_fields = ('report_sem1_sent', 'report_sem2_sent', 'mentor_indemn')
    fieldsets = [
        (None, {
            'fields': (
                ('last_name', 'first_name', 'ext_id'), ('street', 'pcode', 'city', 'district'),
                ('email', 'tel', 'mobile'), ('gender', 'avs', 'birth_date'),
                ('archived', 'dispense_ecg', 'dispense_eps', 'soutien_dys'),
                ('klass', 'option_ase'),
                ('report_sem1', 'report_sem1_sent'),
                ('report_sem2', 'report_sem2_sent'),
                ('corporation', 'instructor', 'instructor2')
            )}
        ),
        ("Procédure de qualification", {
            'classes': ['collapse'],
            'fields': (
                        ('supervisor',  'supervision_attest_received'),
                        ('subject', 'title'),
                        ('training_referent', 'referent'),
                        ('mentor', 'mentor_indemn'),
                      )
        }),
    ]
    actions = ['archive']
    inlines = [ExaminationInline, SupervisionBillInline]

    def mentor_indemn(self, obj):
        if obj is None or not obj.mentor:
            return '-'
        return format_html(
            '<a class="button" href="{}">Indemnité au mentor</a>',
            reverse('print-mentor-compens-form', args=[obj.pk]),
        )
    mentor_indemn.short_description = 'Indemnité'

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        inlines = super().get_inlines(request, obj=obj)
        # SupervisionBillInline is only adequate for EDE students
        if not obj.klass or obj.klass.section.name != 'EDE':
            inlines = [inl for inl in inlines if inl != SupervisionBillInline]
        if not obj.is_ede() and not obj.is_eds():
            inlines = [inl for inl in inlines if inl != ExaminationInline]
        if request.method == 'POST':
            # Special case where inlines would be different before and after POST
            if SupervisionBillInline in inlines and not 'supervisionbill_set-TOTAL_FORMS' in request.POST:
                inlines.remove(SupervisionBillInline)
            if ExaminationInline in inlines and not 'examination_set-TOTAL_FORMS' in request.POST:
                inlines.remove(ExaminationInline)
        return inlines

    def get_fieldsets(self, request, obj=None):
        if not obj or (not obj.is_ede() and not obj.is_eds()):
            # Hide group "Procédure de qualification"
            fieldsets = deepcopy(self.fieldsets)
            fieldsets[1][1]['classes'] = ['hidden']
            return fieldsets
        return super().get_fieldsets(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        ffield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name in self.autocomplete_fields:
            ffield.widget.attrs.update({'data-minimum-input-length': 3})
        return ffield

    def archive(self, request, queryset):
        for student in queryset:
            # Save each item individually to allow for custom save() logic.
            student.archived = True
            student.save()
    archive.short_description = "Marquer les étudiants sélectionnés comme archivés"


class CorpContactAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'corporation', 'role')
    list_filter = (('archived', ArchivedListFilter),)
    ordering = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'role')
    fields = (('civility', 'last_name', 'first_name'),
              ('street', 'pcode', 'city'),
              ('birth_date', 'nation'),
              ('corporation',),
              ('sections', 'is_main', 'always_cc', 'archived'),
              ('role', 'ext_id'), ('tel', 'email'), ('avs',),
              ('iban', 'bank', 'clearing' ),
              ('qualification', 'fields_of_interest'),
             )
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.base_fields['sections'].widget.can_add_related = False
        return form

    def get_search_results(self, request, qs, term):
        qs, distinct = super().get_search_results(request, qs, term)
        return qs.exclude(archived=True), distinct


class ContactInline(admin.StackedInline):
    model = CorpContact
    fields = (('civility', 'last_name', 'first_name'),
              ('sections', 'is_main', 'always_cc', 'archived'),
              ('role', 'tel', 'email'))
    extra = 1
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }


class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'pcode', 'city', 'district', 'ext_id')
    list_editable = ('short_name',)  # Temporarily?
    list_filter = (('archived', ArchivedListFilter),)
    search_fields = ('name', 'street', 'pcode', 'city')
    ordering = ('name',)
    fields = (
        ('name', 'short_name'),
        'parent',
        ('sector', 'typ', 'ext_id'),
        'street',
        ('pcode', 'city', 'district'),
        ('tel', 'email'),
        'web',
        'archived',
    )
    inlines = [ContactInline]
    actions = ['export_corporations']

    def get_search_results(self, request, qs, term):
        qs, distinct = super().get_search_results(request, qs, term)
        return qs.exclude(archived=True), distinct

    def export_corporations(self, request, queryset):
        """
        Export all Corporations in Excel file.
        """
        export_fields = OrderedDict([
            (getattr(f, 'verbose_name', f.name), f.name)
            for f in Corporation._meta.get_fields() if f.name in (
                'name', 'short_name', 'sector', 'typ', 'street', 'pcode',
                'city', 'district', 'tel', 'email', 'web', 'ext_id', 'archived'
            )
        ])
        export = OpenXMLExport('Exportation')
        export.write_line(export_fields.keys(), bold=True)
        for corp in queryset.values_list(*export_fields.values()):
            values = []
            for value, field_name in zip(corp, export_fields.values()):
                if field_name == 'archived':
                    value = 'Oui' if value else ''
                values.append(value)
            export.write_line(values)
        return export.get_http_response('corporations_export')
    export_corporations.short_description = 'Exportation Excel'


class AvailabilityAdminForm(forms.ModelForm):
    """
    Custom avail form to create several availabilities at once when inlined in
    the PeriodAdmin interface
    """
    num_avail = forms.IntegerField(label="Nombre de places", initial=1, required=False)

    class Media:
        js = ('admin/js/jquery.init.js', 'js/avail_form.js',)

    class Meta:
        model = Availability
        fields = '__all__'
        widgets = {
            'num_avail': forms.TextInput(attrs={'size': 3}),
        }

    def __init__(self, data=None, files=None, **kwargs):
        super().__init__(data=data, files=files, **kwargs)
        if self.instance.pk is not None:
            # Hide num_avail on existing instances
            self.fields['num_avail'].widget = forms.HiddenInput()
        # Limit CorpContact objects to contacts of chosen corporation
        if data is None and self.instance.corporation_id:
            self.fields['contact'].queryset = self.instance.corporation.corpcontact_set

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        # Create supplementary availabilities depending on num_avail
        num_avail = self.cleaned_data.get('num_avail', 1) or 1
        for i in range(1, num_avail):
            Availability.objects.create(
                corporation=instance.corporation,
                period=instance.period,
                domain=instance.domain,
                contact=instance.contact,
                comment=instance.comment)
        return instance


class AvailabilityInline(admin.StackedInline):
    model = Availability
    form = AvailabilityAdminForm
    ordering = ('corporation__name',)
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows':2, 'cols':40})},
    }
    autocomplete_fields = ['corporation']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        ffield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name in self.autocomplete_fields:
            ffield.widget.attrs.update({'data-minimum-input-length': 3})
        return ffield


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('title', 'dates', 'section', 'level')
    list_filter = ('section', 'level')
    inlines = [AvailabilityInline]


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('corporation', 'period', 'domain', 'contact')
    list_filter = ('period',)
    fields = (('corporation', 'period'), 'domain', 'contact', 'priority', 'comment')
    form = AvailabilityAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "corporation":
            kwargs["queryset"] = Corporation.objects.filter(archived=False).order_by('name')
        if db_field.name == "contact":
            kwargs["queryset"] = CorpContact.objects.filter(archived=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TrainingAdmin(admin.ModelAdmin):
    search_fields = ('student__first_name', 'student__last_name', 'availability__corporation__name')
    raw_id_fields = ('availability',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "referent":
            kwargs["queryset"] = Teacher.objects.filter(archived=False).order_by('last_name', 'first_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'public', 'subject', 'period', 'imputation')
    list_filter = ('imputation', )
    search_fields = ('teacher__last_name', 'public', 'subject')



class GroupAdmin(AuthGroupAdmin):
    list_display = ['name', 'membres']

    def membres(self, grp):
        return format_html_join(', ', '<a href="{}">{}</a>', [
            (reverse('admin:auth_user_change', args=(user.pk,)), user.username)
            for user in grp.user_set.all().order_by('username')
        ])


admin.site.register(Section)
admin.site.register(Level)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Option)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentFile)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Corporation, CorporationAdmin)
admin.site.register(CorpContact, CorpContactAdmin)
admin.site.register(Domain)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(LogBookReason)
admin.site.register(LogBook)
admin.site.register(ExamEDESession)
admin.site.register(Examination)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
