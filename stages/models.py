# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Section(models.Model):
    """ Filières """
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Filière"

    def __unicode__(self):
        return self.name


class Student(models.Model):
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    birth_date = models.DateField(verbose_name='Date de naissance')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    section = models.ForeignKey(Section)

    class Meta:
        verbose_name = "Étudiant"

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)


class Referent(models.Model):
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')

    class Meta:
        verbose_name = "Référent"

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)


class Corporation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    street = models.CharField(max_length=100, verbose_name='Rue')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    tel = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.CharField(max_length=40, blank=True, verbose_name='Courriel')

    class Meta:
        verbose_name = "Institution"

    def __unicode__(self):
        return self.name


class CorpContact(models.Model):
    corporation = models.ForeignKey(Corporation, verbose_name='Institution')
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
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

    def __unicode__(self):
        return self.name


class Period(models.Model):
    """ Périodes de stages """
    section = models.ForeignKey(Section, verbose_name='Filière')
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
    number = models.IntegerField(verbose_name='Nombre de places')
    domain = models.ForeignKey(Domain, verbose_name='Domaine')

    class Meta:
        verbose_name = "Disponibilité"

    def __unicode__(self):
        return '%d place(s) chez %s (%s)' % (self.number, self.corporation, self.period)


class Training(models.Model):
    """ Stages """
    student = models.ForeignKey(Student, verbose_name='Étudiant')
    corporation = models.ForeignKey(Corporation, verbose_name='Institution')
    referent = models.ForeignKey(Referent, verbose_name='Référent')
    period = models.ForeignKey(Period, verbose_name='Période')
    domain = models.ForeignKey(Domain, verbose_name='Domaine')

    class Meta:
        verbose_name = "Stage"

    def __unicode__(self):
        return '%s chez %s (%s)' % (self.student, self.corporation, self.period)
