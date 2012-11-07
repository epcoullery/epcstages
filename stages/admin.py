from django.contrib import admin

from stages.models import (Student, Section, Referent, Corporation, CorpContact,
    Domain, Period, Availability, Training)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'pcode', 'city', 'section')
    list_filter = ('section',)
    fields = (('last_name', 'first_name'), ('pcode', 'city'),
              'birth_date', 'section')


class CorpContactAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'corporation')
    fields = ('corporation', ('last_name', 'first_name'), ('tel', 'email'))

class ContactInline(admin.TabularInline):
    model = CorpContact
    extra = 1

class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'pcode', 'city')
    fields = ('name', 'street', ('pcode', 'city'), ('tel', 'email'))
    inlines = [ContactInline]


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

class PeriodAdmin(admin.ModelAdmin):
    list_display = ('dates', 'section')
    list_filter = ('section',)
    inlines = [AvailabilityInline]


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('corporation', 'period', 'domain')
    list_filter = ('period',)
    fields = (('corporation', 'period'), 'domain', 'comment')


admin.site.register(Student, StudentAdmin)
admin.site.register(Section)
admin.site.register(Referent)
admin.site.register(Corporation, CorporationAdmin)
admin.site.register(CorpContact, CorpContactAdmin)
admin.site.register(Domain)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Training)
