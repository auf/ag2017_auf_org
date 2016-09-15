# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0007_auto_20160907_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalresponse',
            name='txn_id',
            field=models.CharField(max_length=250, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paypalresponse',
            name='type_reponse',
            field=models.CharField(max_length=3, choices=[(b'IPN', 'Instant Payment Notification'), (b'PDT', 'Payment Data Transfer'), (b'CAN', 'Cancelled')]),
        ),
    ]
