# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0003_etablissement_membre'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='code',
            field=models.CharField(default='', unique=True, max_length=255),
            preserve_default=False,
        ),
    ]
