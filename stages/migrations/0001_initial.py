# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Section'
        db.create_table('stages_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('stages', ['Section'])

        # Adding model 'Level'
        db.create_table('stages_level', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('stages', ['Level'])

        # Adding model 'Klass'
        db.create_table('stages_klass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Section'])),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Level'])),
        ))
        db.send_create_signal('stages', ['Klass'])

        # Adding model 'Student'
        db.create_table('stages_student', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ext_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('birth_date', self.gf('django.db.models.fields.DateField')()),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('pcode', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('tel', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('klass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Klass'])),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('stages', ['Student'])

        # Adding model 'Referent'
        db.create_table('stages_referent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('abrev', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('stages', ['Referent'])

        # Adding model 'Corporation'
        db.create_table('stages_corporation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('typ', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('pcode', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('tel', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('web', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('stages', ['Corporation'])

        # Adding model 'CorpContact'
        db.create_table('stages_corpcontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Corporation'])),
            ('is_main', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('tel', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
        ))
        db.send_create_signal('stages', ['CorpContact'])

        # Adding model 'Domain'
        db.create_table('stages_domain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('stages', ['Domain'])

        # Adding model 'Period'
        db.create_table('stages_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Section'])),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Level'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('stages', ['Period'])

        # Adding model 'Availability'
        db.create_table('stages_availability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Corporation'])),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Period'])),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Domain'])),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('stages', ['Availability'])

        # Adding model 'Training'
        db.create_table('stages_training', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Student'])),
            ('availability', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['stages.Availability'], unique=True)),
            ('referent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.Referent'], null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('stages', ['Training'])


    def backwards(self, orm):
        # Deleting model 'Section'
        db.delete_table('stages_section')

        # Deleting model 'Level'
        db.delete_table('stages_level')

        # Deleting model 'Klass'
        db.delete_table('stages_klass')

        # Deleting model 'Student'
        db.delete_table('stages_student')

        # Deleting model 'Referent'
        db.delete_table('stages_referent')

        # Deleting model 'Corporation'
        db.delete_table('stages_corporation')

        # Deleting model 'CorpContact'
        db.delete_table('stages_corpcontact')

        # Deleting model 'Domain'
        db.delete_table('stages_domain')

        # Deleting model 'Period'
        db.delete_table('stages_period')

        # Deleting model 'Availability'
        db.delete_table('stages_availability')

        # Deleting model 'Training'
        db.delete_table('stages_training')


    models = {
        'stages.availability': {
            'Meta': {'object_name': 'Availability'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Corporation']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Period']"})
        },
        'stages.corpcontact': {
            'Meta': {'object_name': 'CorpContact'},
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Corporation']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        'stages.corporation': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Corporation'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pcode': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'typ': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'web': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'stages.domain': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Domain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'stages.klass': {
            'Meta': {'object_name': 'Klass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Level']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Section']"})
        },
        'stages.level': {
            'Meta': {'object_name': 'Level'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'stages.period': {
            'Meta': {'object_name': 'Period'},
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Level']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Section']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'stages.referent': {
            'Meta': {'ordering': "(u'last_name', u'first_name')", 'object_name': 'Referent'},
            'abrev': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'stages.section': {
            'Meta': {'object_name': 'Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'stages.student': {
            'Meta': {'object_name': 'Student'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ext_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Klass']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'pcode': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        'stages.training': {
            'Meta': {'object_name': 'Training'},
            'availability': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['stages.Availability']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Referent']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Student']"})
        }
    }

    complete_apps = ['stages']