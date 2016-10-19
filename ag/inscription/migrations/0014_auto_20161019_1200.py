# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0013_inscription_reseautage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inscription',
            name='type_chambre_hotel',
        ),
    ]
