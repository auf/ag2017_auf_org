# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0008_auto_20160908_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='numero_dossier',
            field=models.CharField(max_length=8, unique=True, null=True),
        ),
    ]
