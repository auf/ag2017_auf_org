# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0006_auto_20160907_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paypalinvoice',
            old_name='tx_id',
            new_name='invoice_uid',
        ),
    ]
