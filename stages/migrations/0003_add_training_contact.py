# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Training.contact'
        db.add_column('stages_training', 'contact',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stages.CorpContact'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Training.contact'
        db.delete_column('stages_training', 'contact_id')


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
            'role': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        'stages.corporation': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Corporation'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
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
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.CorpContact']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Referent']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stages.Student']"})
        }
    }

    complete_apps = ['stages']