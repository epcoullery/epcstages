# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Move training.contact to availability.contact"
        for training in orm.Training.objects.filter(contact__isnull=False):
            training.availability.contact = training.contact
            training.availability.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

    models = {
        u'stages.availability': {
            'Meta': {'object_name': 'Availability'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.CorpContact']", 'null': 'True', 'blank': 'True'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Corporation']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Period']"})
        },
        u'stages.corpcontact': {
            'Meta': {'object_name': 'CorpContact'},
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Corporation']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'stages.corporation': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Corporation'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'pcode': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'typ': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'web': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'stages.domain': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Domain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'stages.klass': {
            'Meta': {'object_name': 'Klass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Level']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Section']"})
        },
        u'stages.level': {
            'Meta': {'object_name': 'Level'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'stages.period': {
            'Meta': {'ordering': "(u'-start_date',)", 'object_name': 'Period'},
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Level']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Section']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'stages.referent': {
            'Meta': {'ordering': "(u'last_name', u'first_name')", 'object_name': 'Referent'},
            'abrev': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'stages.section': {
            'Meta': {'object_name': 'Section'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'stages.student': {
            'Meta': {'object_name': 'Student'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ext_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Klass']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'pcode': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'stages.training': {
            'Meta': {'object_name': 'Training'},
            'availability': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['stages.Availability']", 'unique': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.CorpContact']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Referent']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stages.Student']"})
        }
    }

    complete_apps = ['stages']
    symmetrical = True
