# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0011_auto_20160923_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='nom',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invitation',
            name='prenom',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
