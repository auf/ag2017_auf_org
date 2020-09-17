# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inscription',
            name='arrivee_compagnie',
        ),
        migrations.RemoveField(
            model_name='inscription',
            name='depart_compagnie',
        ),
    ]
