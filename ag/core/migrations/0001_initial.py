# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EtablissementDelinquant',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'id')),
            ],
        ),
    ]
