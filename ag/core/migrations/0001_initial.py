# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EtablissementDelinquant'
        db.create_table('core_etablissementdelinquant', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='id')),
        ))
        db.send_create_signal('core', ['EtablissementDelinquant'])

    def backwards(self, orm):
        # Deleting model 'EtablissementDelinquant'
        db.delete_table('core_etablissementdelinquant')

    models = {
        'core.etablissementdelinquant': {
            'Meta': {'object_name': 'EtablissementDelinquant'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'id'"})
        }
    }

    complete_apps = ['core']