# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0012_auto_20160926_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='reseautage',
            field=models.BooleanField(default=False),
        ),
    ]
