# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Video.description'
        db.add_column('outil_video', 'description',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)