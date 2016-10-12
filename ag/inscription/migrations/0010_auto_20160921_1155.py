# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0009_inscription_numero_dossier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalresponse',
            name='invoice_uid',
            field=models.UUIDField(db_index=True),
        ),
    ]
