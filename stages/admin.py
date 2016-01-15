from django import forms
from django.contrib import admin
from django.db import models

from stages.models import (Student, Section, Level, Klass, Referent, Corporation,
    CorpContact, Domain, Period, Availability, Training)


class KlassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'level')
    ordering = ('name',)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'pcode', 'city', 'klass', 'archived')
    ordering = ('last_name', 'first_name')
    list_filter = ('klass', 'archived')
    search_fields = ('last_name', 'first_name', 'pcode', 'city', 'klass__name')
    fields = (('last_name', 'first_name'), 'street', ('pcode', 'city'), 'email',
              ('tel', 'mobile'), ('birth_date', 'ext_id'), 'klass', 'archived')
    readonly_fields = ('ext_id',)
    actions = ['archive']

    def archive(self, request, queryset):
        queryset.update(archived=True)
    archive.short_description = "Marquer les étudiants sélectionnés comme archivés"

    '''def get_readonly_fields(self, request, obj=None):
        if 'edit' not in request.GET:
            return self.fields
        else:
            return self.readonly_fields
    '''


class ReferentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'abrev', 'email')


class CorpContactAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'corporation', 'role')
    ordering = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'role')
    fields = (('corporation',), ('sections', 'is_main', 'always_cc'),
              ('title', 'last_name', 'first_name'),
              'role', ('tel', 'email'))
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.base_fields['sections'].widget.can_add_related = False
        return form


class ContactInline(admin.StackedInline):
    model = CorpContact
    fields = (('sections', 'is_main', 'always_cc'),
              ('title', 'last_name', 'first_name'),
              ('role', 'tel', 'email'))
    extra = 1
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }


class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'pcode', 'city')
    list_editable = ('short_name',)  # Temporarily?
    search_fields = ('name', 'pcode', 'city')
    ordering = ('name',)
    fields = (('name', 'short_name', 'sector'), ('typ', 'ext_id'), 'street', ('pcode', 'city'), ('tel', 'email'),
              'web', 'archived')
    inlines = [ContactInline]


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

class AvailabilityInline(admin.TabularInline):
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
    fields = (('corporation', 'period'), 'domain', 'contact', 'comment')
    form = AvailabilityAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "corporation":
            kwargs["queryset"] = Corporation.objects.filter(archived=False).order_by('name')
        return super(AvailabilityAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TrainingAdmin(admin.ModelAdmin):
    search_fields = ('student__first_name', 'student__last_name', 'availability__corporation__name')
    raw_id_fields = ('availability',)


admin.site.register(Section)
admin.site.register(Level)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Referent, ReferentAdmin)
admin.site.register(Corporation, CorporationAdmin)
admin.site.register(CorpContact, CorpContactAdmin)
admin.site.register(Domain)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Training, TrainingAdmin)
