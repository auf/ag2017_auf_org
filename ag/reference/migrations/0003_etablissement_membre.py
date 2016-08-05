# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0002_pays_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='etablissement',
            name='membre',
            field=models.BooleanField(default=False),
        ),
    ]
