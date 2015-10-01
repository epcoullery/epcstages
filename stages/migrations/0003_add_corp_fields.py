# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0002_corpcontact_ext_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporation',
            name='ext_id',
            field=models.IntegerField(verbose_name='ID externe', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='corporation',
            name='sector',
            field=models.CharField(max_length=40, verbose_name='Secteur', blank=True),
        ),
        migrations.AddField(
            model_name='corporation',
            name='short_name',
            field=models.CharField(max_length=40, verbose_name='Nom court', blank=True),
        ),
    ]
