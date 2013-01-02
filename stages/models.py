# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Section(models.Model):
    """ Filières """
    name = models.CharField(max_length=20, verbose_name='Nom')

    class Meta:
        verbose_name = "Filière"

    def __unicode__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=10, verbose_name='Nom')

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

    def __unicode__(self):
        return self.name


class Klass(models.Model):
    name = models.CharField(max_length=10, verbose_name='Nom')
    section = models.ForeignKey(Section, verbose_name='Filière')
    level = models.ForeignKey(Level, verbose_name='Niveau')

    class Meta:
        verbose_name = "Classe"

    def __unicode__(self):
        return self.name


class Student(models.Model):
    ext_id = models.IntegerField(null=True, unique=True, verbose_name='ID externe')
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    birth_date = models.DateField(verbose_name='Date de naissance')
    street = models.CharField(max_length=150, blank=True, verbose_name='Rue')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    tel = models.CharField(max_length=40, blank=True, verbose_name='Téléphone')
    mobile = models.CharField(max_length=40, blank=True, verbose_name='Portable')
    email = models.EmailField(verbose_name='Courriel', blank=True)
    klass = models.ForeignKey(Klass, verbose_name='Classe')
    archived = models.BooleanField(default=False, verbose_name='Archivé')

    support_tabimport = True

    class Meta:
        verbose_name = "Étudiant"

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    @classmethod
    def prepare_import(cls, values):
        ''' Hook for tabimport, before new object get created '''
        if 'klass' in values:
            try:
                k = Klass.objects.get(name=values['klass'])
            except Klass.DoesNotExist:
                raise Exception("La classe '%s' n'existe pas encore" % values['klass'])
            values['klass'] = k
        if 'city' in values and is_int(values['city'][:4]):
            values['pcode'], _, values['city'] = values['city'].partition(' ')
        return values


class Referent(models.Model):
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    abrev = models.CharField(max_length=10, blank=True, verbose_name='Initiales')
    archived = models.BooleanField(default=False, verbose_name='Archivé')

    support_tabimport = True

    class Meta:
        verbose_name = "Référent"
        ordering = ('last_name', 'first_name')

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)


class Corporation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    typ = models.CharField(max_length=40, blank=True, verbose_name='Type de structure')
    street = models.CharField(max_length=100, blank=True, verbose_name='Rue')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    tel = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, verbose_name='Courriel')
    web = models.URLField(blank=True, verbose_name='Site Web')
    archived = models.BooleanField(default=False, verbose_name='Archivé')

    class Meta:
        verbose_name = "Institution"
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class CorpContact(models.Model):
    corporation = models.ForeignKey(Corporation, verbose_name='Institution')
    is_main = models.BooleanField(default=False, verbose_name='Contact principal')
    title = models.CharField(max_length=40, blank=True, verbose_name='Civilité')
    first_name = models.CharField(max_length=40, blank=True, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    role = models.CharField(max_length=40, verbose_name='Fonction')
    tel = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.CharField(max_length=40, blank=True, verbose_name='Courriel')

    class Meta:
        verbose_name = "Contact"

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)


class Domain(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nom')

    class Meta:
        verbose_name = "Domaine"
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Period(models.Model):
    """ Périodes de stages """
    title = models.CharField(max_length=150, verbose_name='Titre')
    section = models.ForeignKey(Section, verbose_name='Filière')
    level = models.ForeignKey(Level, verbose_name='Niveau')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')

    class Meta:
        verbose_name = "Période de stage"

    def __unicode__(self):
        return '%s (filière %s)' % (self.dates, self.section)

    @property
    def dates(self):
        return '%s - %s' % (self.start_date, self.end_date)


class Availability(models.Model):
    """ Disponibilités des institutions """
    corporation = models.ForeignKey(Corporation, verbose_name='Institution')
    period = models.ForeignKey(Period, verbose_name='Période')
    domain = models.ForeignKey(Domain, verbose_name='Domaine')
    comment = models.TextField(blank=True, verbose_name='Remarques')

    class Meta:
        verbose_name = "Disponibilité"

    def __unicode__(self):
        return '%s - %s (%s)' % (self.period, self.corporation, self.domain)

    @property
    def free(self):
        try:
            self.training
        except Training.DoesNotExist:
            return True
        return False


class Training(models.Model):
    """ Stages """
    student = models.ForeignKey(Student, verbose_name='Étudiant')
    availability = models.OneToOneField(Availability, verbose_name='Disponibilité')
    referent = models.ForeignKey(Referent, null=True, blank=True, verbose_name='Référent')
    comment = models.TextField(blank=True, verbose_name='Remarques')

    class Meta:
        verbose_name = "Stage"

    def __unicode__(self):
        return '%s chez %s (%s)' % (self.student, self.availability.corporation, self.availability.period)
