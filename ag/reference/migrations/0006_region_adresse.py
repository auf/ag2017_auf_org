# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0005_auto_20160829_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='adresse',
            field=models.TextField(null=True),
        ),
    ]
