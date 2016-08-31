# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(verbose_name='Remarques', blank=True)),
            ],
            options={
                'verbose_name': 'Disponibilité',
            },
        ),
        migrations.CreateModel(
            name='CorpContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_main', models.BooleanField(default=False, verbose_name='Contact principal')),
                ('always_cc', models.BooleanField(default=False, verbose_name='Toujours en copie')),
                ('title', models.CharField(max_length=40, verbose_name='Civilité', blank=True)),
                ('first_name', models.CharField(max_length=40, verbose_name='Prénom', blank=True)),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('role', models.CharField(max_length=40, verbose_name='Fonction', blank=True)),
                ('tel', models.CharField(max_length=20, verbose_name='Téléphone', blank=True)),
                ('email', models.CharField(max_length=40, verbose_name='Courriel', blank=True)),
            ],
            options={
                'verbose_name': 'Contact',
            },
        ),
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Nom')),
                ('typ', models.CharField(max_length=40, verbose_name='Type de structure', blank=True)),
                ('street', models.CharField(max_length=100, verbose_name='Rue', blank=True)),
                ('pcode', models.CharField(max_length=4, verbose_name='Code postal')),
                ('city', models.CharField(max_length=40, verbose_name='Localité')),
                ('tel', models.CharField(max_length=20, verbose_name='Téléphone', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Courriel', blank=True)),
                ('web', models.URLField(verbose_name='Site Web', blank=True)),
                ('archived', models.BooleanField(default=False, verbose_name='Archivé')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Institution',
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Nom')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Domaine',
            },
        ),
        migrations.CreateModel(
            name='Klass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Classe',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Niveau',
                'verbose_name_plural': 'Niveaux',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name='Titre')),
                ('start_date', models.DateField(verbose_name='Date de début')),
                ('end_date', models.DateField(verbose_name='Date de fin')),
                ('level', models.ForeignKey(verbose_name='Niveau', to='stages.Level', on_delete=models.PROTECT)),
            ],
            options={
                'ordering': ('-start_date',),
                'verbose_name': 'Période de stage',
            },
        ),
        migrations.CreateModel(
            name='Referent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=40, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('abrev', models.CharField(max_length=10, verbose_name='Initiales', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Courriel', blank=True)),
                ('archived', models.BooleanField(default=False, verbose_name='Archivé')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
                'verbose_name': 'Référent',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Filière',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ext_id', models.IntegerField(unique=True, null=True, verbose_name='ID externe')),
                ('first_name', models.CharField(max_length=40, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('birth_date', models.DateField(verbose_name='Date de naissance')),
                ('street', models.CharField(max_length=150, verbose_name='Rue', blank=True)),
                ('pcode', models.CharField(max_length=4, verbose_name='Code postal')),
                ('city', models.CharField(max_length=40, verbose_name='Localité')),
                ('tel', models.CharField(max_length=40, verbose_name='Téléphone', blank=True)),
                ('mobile', models.CharField(max_length=40, verbose_name='Portable', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Courriel', blank=True)),
                ('archived', models.BooleanField(default=False, verbose_name='Archivé')),
                ('klass', models.ForeignKey(verbose_name='Classe', to='stages.Klass', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': '\xc9tudiant',
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(verbose_name='Remarques', blank=True)),
                ('availability', models.OneToOneField(verbose_name='Disponibilité', to='stages.Availability', on_delete=models.CASCADE)),
                ('referent', models.ForeignKey(verbose_name='Référent', blank=True, to='stages.Referent', null=True, on_delete=models.SET_NULL)),
                ('student', models.ForeignKey(verbose_name='\xc9tudiant', to='stages.Student', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Stage',
            },
        ),
        migrations.AddField(
            model_name='period',
            name='section',
            field=models.ForeignKey(verbose_name='Filière', to='stages.Section', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='klass',
            name='level',
            field=models.ForeignKey(verbose_name='Niveau', to='stages.Level', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='klass',
            name='section',
            field=models.ForeignKey(verbose_name='Filière', to='stages.Section', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='corporation',
            field=models.ForeignKey(verbose_name='Institution', to='stages.Corporation', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='availability',
            name='contact',
            field=models.ForeignKey(verbose_name='Contact institution', blank=True, to='stages.CorpContact', null=True, on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='availability',
            name='corporation',
            field=models.ForeignKey(verbose_name='Institution', to='stages.Corporation', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='availability',
            name='domain',
            field=models.ForeignKey(verbose_name='Domaine', to='stages.Domain', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='availability',
            name='period',
            field=models.ForeignKey(verbose_name='Période', to='stages.Period', on_delete=models.CASCADE),
        ),
    ]
