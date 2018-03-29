import os
import tempfile
import zipfile

from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Case, Count, When
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Teacher, Option, Student, Section, Level, Klass, Corporation,
    CorpContact, Domain, Period, Availability, Training, Course,
    LogBookReason, LogBook, ExamEDESession
)
from .pdf import ChargeSheetPDF


def print_charge_sheet(modeladmin, request, queryset):
    """
    Génère un pdf pour chaque enseignant, écrit le fichier créé
    dans une archive et renvoie une archive de pdf
    """
    filename = 'archive_FeuillesDeCharges.zip'
    path = os.path.join(tempfile.gettempdir(), filename)

    with zipfile.ZipFile(path, mode='w', compression=zipfile.ZIP_DEFLATED) as filezip:
        for teacher in queryset:
            activities = teacher.calc_activity()
            pdf = ChargeSheetPDF(teacher)
            pdf.produce(activities)
            filezip.write(pdf.filename)

    with open(filezip.filename, mode='rb') as fh:
        response = HttpResponse(fh.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    return response

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
            (k.pk, k.name) for k in Klass.objects.annotate(
                num_students=Count(Case(When(student__archived=False, then=1)))
            ).filter(num_students__gt=0).order_by('name')
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
    inlines = [StudentInline]


class LogBookInline(admin.TabularInline):
    model = LogBook
    ordering = ('input_date',)
    fields = ('start_date', 'end_date', 'reason', 'comment', 'nb_period')
    extra = 0


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'abrev', 'email', 'contract', 'rate', 'total_logbook', 'archived')
    list_filter = (('archived', ArchivedListFilter), 'contract')
    fields = (('civility', 'last_name', 'first_name', 'abrev'),
              ('birth_date', 'email', 'ext_id'),
              ('contract', 'rate', 'archived'),
              ('previous_report', 'next_report', 'total_logbook'))
    readonly_fields = ('total_logbook',)
    actions = [print_charge_sheet]
    inlines = [LogBookInline]


class StudentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'pcode', 'city', 'klass', 'archived')
    ordering = ('last_name', 'first_name')
    list_filter = (('archived', ArchivedListFilter), ('klass', KlassRelatedListFilter))
    search_fields = ('last_name', 'first_name', 'pcode', 'city', 'klass__name')
    autocomplete_fields = ('corporation', 'instructor', 'supervisor', 'mentor', 'expert')
    readonly_fields = ('report_sem1_sent', 'report_sem2_sent', 'examination_actions')
    fieldsets = (
        (None, {
            'fields': (('last_name', 'first_name', 'ext_id'), ('street', 'pcode', 'city', 'district'),
                      ('email', 'tel', 'mobile'), ('gender', 'avs', 'birth_date'),
                      ('archived', 'dispense_ecg', 'dispense_eps', 'soutien_dys'),
                      ('klass', 'option_ase'),
                      ('report_sem1', 'report_sem1_sent'),
                      ('report_sem2', 'report_sem2_sent'),
                      ('corporation', 'instructor',)
                      )
                }
         ),
        ("Examen Qualification EDE", {
            'classes': ('collapse',),
            'fields': (
                        ('supervisor', ),
                        ('subject', 'title'),
                        ('training_referent', 'referent', 'mentor'),
                        ('internal_expert', 'expert'),
                        ('session', 'date_exam', 'room', 'mark'),
                        ('examination_actions',)
                      )
        }),
    )
    actions = ['archive']
    def archive(self, request, queryset):
        for student in queryset:
            # Save each item individually to allow for custom save() logic.
            student.archived = True
            student.save()
    archive.short_description = "Marquer les étudiants sélectionnés comme archivés"

    def examination_actions(self, obj):
        if obj.klass.section.name == 'EDE' and obj.klass.level.name == "3":
            return format_html(
                '<a class="button" href="{}">Courrier pour l\'expert</a>&nbsp;'
                '<a class="button" href="{}">Mail convocation soutenance</a>&nbsp;'
                '<a class="button" href="{}">Indemnité aux experts</a>',
                reverse('print-pdf-to-expert-ede', args=[obj.pk]),
                reverse('student-ede-convocation', args=[obj.pk]),
                reverse('examination_compensation', args=[obj.pk])
            )
        else:
            return ''
    examination_actions.short_description = 'Actions pour les examens EDE'
    examination_actions.allow_tags = True


class CorpContactAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'corporation', 'role')
    list_filter = (('archived', ArchivedListFilter),)
    ordering = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'role')
    fields = (('title', 'last_name', 'first_name'),
              ('street', 'pcode', 'city'),
              ('birth_date',),
              ('corporation',),
              ('sections', 'is_main', 'always_cc', 'archived'),
              ('role', 'ext_id'), ('tel', 'email'),
              ('ccp', 'bank', 'clearing' ),
              ('iban',),
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
    fields = (('title', 'last_name', 'first_name'),
              ('sections', 'is_main', 'always_cc', 'archived'),
              ('role', 'tel', 'email'))
    extra = 1
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }


class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'pcode', 'city', 'ext_id')
    list_editable = ('short_name',)  # Temporarily?
    list_filter = (('archived', ArchivedListFilter),)
    search_fields = ('name', 'street', 'pcode', 'city')
    ordering = ('name',)
    fields = (('name', 'short_name'), 'parent', ('sector', 'typ', 'ext_id'),
              'street', ('pcode', 'city'), ('tel', 'email'), 'web', 'archived')
    inlines = [ContactInline]

    def get_search_results(self, request, qs, term):
        qs, distinct = super().get_search_results(request, qs, term)
        return qs.exclude(archived=True), distinct


class AvailabilityAdminForm(forms.ModelForm):
    """
    Custom avail form to create several availabilities at once when inlined in
    the PeriodAdmin interface
    """
    num_avail = forms.IntegerField(label="Nombre de places", initial=1, required=False)

    class Media:
        js = ('js/avail_form.js',)

    class Meta:
        model = Availability
        fields = '__all__'
        widgets = {
            'num_avail': forms.TextInput(attrs={'size': 3}),
        }

    def __init__(self, data=None, files=None, **kwargs):
        super(AvailabilityAdminForm, self).__init__(data=data, files=files, **kwargs)
        if self.instance.pk is not None:
            # Hide num_avail on existing instances
            self.fields['num_avail'].widget = forms.HiddenInput()
        # Limit CorpContact objects to contacts of chosen corporation
        if data is None and self.instance.corporation_id:
            self.fields['contact'].queryset = self.instance.corporation.corpcontact_set

    def save(self, **kwargs):
        instance = super(AvailabilityAdminForm, self).save(**kwargs)
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


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('title', 'dates', 'section', 'level')
    list_filter = ('section', 'level')
    inlines = [AvailabilityInline]


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('corporation', 'period', 'domain')
    list_filter = ('period',)
    fields = (('corporation', 'period'), 'domain', 'contact', 'priority', 'comment')
    form = AvailabilityAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "corporation":
            kwargs["queryset"] = Corporation.objects.filter(archived=False).order_by('name')
        if db_field.name == "contact":
            kwargs["queryset"] = CorpContact.objects.filter(archived=False)
        return super(AvailabilityAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TrainingAdmin(admin.ModelAdmin):
    search_fields = ('student__first_name', 'student__last_name', 'availability__corporation__name')
    raw_id_fields = ('availability',)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'public', 'subject', 'period', 'imputation')
    list_filter = ('imputation', )
    search_fields = ('teacher__last_name', 'public', 'subject')


admin.site.register(Section)
admin.site.register(Level)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Option)
admin.site.register(Student, StudentAdmin)
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
