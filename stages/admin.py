from django.contrib import admin

from stages.models import (Student, Section, Klass, Referent, Corporation, CorpContact,
    Domain, Period, Availability, Training)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'pcode', 'city', 'klass')
    list_filter = ('klass',)
    search_fields = ('last_name', 'first_name', 'pcode', 'city', 'klass')
    fields = (('last_name', 'first_name'), ('pcode', 'city'),
              'birth_date', 'klass', 'archived')


class CorpContactAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'corporation', 'role')
    fields = ('corporation', ('title', 'last_name', 'first_name'),
              'role', ('tel', 'email'))

class ContactInline(admin.StackedInline):
    model = CorpContact
    fields = (('title', 'last_name', 'first_name'),
              ('role', 'tel', 'email'))
    extra = 1

class CorporationAdmin(admin.ModelAdmin):
    list_display = ('name', 'pcode', 'city')
    search_fields = ('name', 'pcode', 'city')
    fields = ('name', 'typ', 'street', ('pcode', 'city'), ('tel', 'email'),
              'web', 'archived')
    inlines = [ContactInline]


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

class PeriodAdmin(admin.ModelAdmin):
    list_display = ('title', 'dates', 'section')
    list_filter = ('section',)
    inlines = [AvailabilityInline]


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('corporation', 'period', 'domain')
    list_filter = ('period',)
    fields = (('corporation', 'period'), 'domain', 'comment')


admin.site.register(Section)
admin.site.register(Klass)
admin.site.register(Student, StudentAdmin)
admin.site.register(Referent)
admin.site.register(Corporation, CorporationAdmin)
admin.site.register(CorpContact, CorpContactAdmin)
admin.site.register(Domain)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Training)
