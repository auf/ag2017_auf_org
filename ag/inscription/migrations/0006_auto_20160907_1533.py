# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0005_paypalinvoice_inscription'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paypalresponse',
            old_name='tx_id',
            new_name='invoice_uid',
        ),
        migrations.AddField(
            model_name='paypalresponse',
            name='txn_id',
            field=models.CharField(default='', max_length=250, db_index=True),
            preserve_default=False,
        ),
    ]
