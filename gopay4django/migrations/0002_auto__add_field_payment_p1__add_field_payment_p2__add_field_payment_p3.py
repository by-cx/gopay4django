# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Payment.p1'
        db.add_column('gopay4django_payment', 'p1',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Payment.p2'
        db.add_column('gopay4django_payment', 'p2',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Payment.p3'
        db.add_column('gopay4django_payment', 'p3',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Payment.p4'
        db.add_column('gopay4django_payment', 'p4',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Payment.p1'
        db.delete_column('gopay4django_payment', 'p1')

        # Deleting field 'Payment.p2'
        db.delete_column('gopay4django_payment', 'p2')

        # Deleting field 'Payment.p3'
        db.delete_column('gopay4django_payment', 'p3')

        # Deleting field 'Payment.p4'
        db.delete_column('gopay4django_payment', 'p4')


    models = {
        'gopay4django.payment': {
            'Meta': {'object_name': 'Payment'},
            '_payment_command': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            '_payment_status': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'p1': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'p2': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'p3': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'p4': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gopay4django']