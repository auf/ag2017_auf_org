# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def delete_chambres(apps, schema_editor):
    Chambre = apps.get_model('gestion', 'Chambre')
    Chambre.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_auto_20161130_1732'),
    ]

    operations = [
        migrations.RunPython(delete_chambres)
    ]
