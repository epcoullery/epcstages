# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='ext_id',
            field=models.IntegerField(verbose_name='ID externe', blank=True, null=True),
        ),
    ]
