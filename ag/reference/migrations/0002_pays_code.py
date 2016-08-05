# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pays',
            name='code',
            field=models.CharField(default='', unique=True, max_length=2),
            preserve_default=False,
        ),
    ]
