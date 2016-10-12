# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0010_auto_20160921_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalresponse',
            name='invoice_uid',
            field=models.UUIDField(null=True, db_index=True),
        ),
    ]
