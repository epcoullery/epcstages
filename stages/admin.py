from django import forms
from django.contrib import admin
from django.db import models

from stages.models import (Student, Section, Level, Klass, Referent, Corporation,
    CorpContact, Domain, Period, Availability, Training)


class KlassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'level')
    ordering = ('name',)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'pcode', 'city', 'klass')
    ordering = ('last_name', 'first_name')
    list_filter = ('klass',)
    search_fields = ('last_name', 'first_name', 'pcode', 'city', 'klass')
    fields = (('last_name', 'first_name'), 'street', ('pcode', 'city'), 'email',
              ('tel', 'mobile'), 'birth_date', 'klass', 'archived')

    '''def get_readonly_fields(self, request, obj=None):
        if 'edit' not in request.GET:
            return self.fields
        else:
            return self.readonly_fields
    '''


class ReferentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'abrev')


class CorpContactAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'corporation', 'role')
    fields = (('corporation', 'is_main'), ('title', 'last_name', 'first_name'),
              'role', ('tel', 'email'))

class ContactInline(admin.StackedInline):
    model = CorpContact
    fields = ('is_main', ('title', 'last_name', 'first_name'),
              ('role', 'tel', 'email'))
    extra = 1

class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'pcode', 'city')
    search_fields = ('name', 'pcode', 'city')
    ordering = ('name',)
    fields = ('name', 'typ', 'street', ('pcode', 'city'), ('tel', 'email'),
              'web', 'archived')
    inlines = [ContactInline]


class AvailabilityAdminForm(forms.ModelForm):
    """
    Custom avail form to create several availabilities at once when inlined in
    the PeriodAdmin interface
    """
    num_avail = forms.IntegerField(label="Nombre de places", initial=1)
    class Meta:
        model = Availability
        widgets = {
            'num_avail': forms.TextInput(attrs={'size': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(AvailabilityAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            # Hide num_avail on existing instances
            self.fields['num_avail'].widget = forms.HiddenInput()

    def save(self, **kwargs):
        instance = super(AvailabilityAdminForm, self).save(**kwargs)
        # Create supplementary availabilities depending on num_avail
        for i in range(1, self.cleaned_data.get('num_avail', 1)):
            Availability.objects.create(
                corporation=instance.corporation,
                period=instance.period,
                domain=instance.domain,
                comment=instance.comment)
        return instance

class AvailabilityInline(admin.TabularInline):
    model = Availability
    form = AvailabilityAdminForm
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
    fields = (('corporation', 'period'), 'domain', 'comment')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "corporation":
            kwargs["queryset"] = Corporation.objects.filter(archived=False).order_by('name')
        return super(AvailabilityAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TrainingAdmin(admin.ModelAdmin):
    search_fields = ('student__first_name', 'student__last_name', 'availability__corporation__name')


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
