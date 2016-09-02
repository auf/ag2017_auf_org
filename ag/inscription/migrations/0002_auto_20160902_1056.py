# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inscription',
            name='programmation_soiree_interconsulaire',
        ),
        migrations.RemoveField(
            model_name='inscription',
            name='programmation_soiree_interconsulaire_invite',
        ),
        migrations.RemoveField(
            model_name='inscription',
            name='programmation_soiree_unesp',
        ),
        migrations.RemoveField(
            model_name='inscription',
            name='programmation_soiree_unesp_invite',
        ),
        migrations.AddField(
            model_name='inscription',
            name='forfait_invite_dejeuners',
            field=models.BooleanField(default=False, verbose_name='Forfait 3 D\xe9jeuners (9,10 et 11)'),
        ),
        migrations.AddField(
            model_name='inscription',
            name='forfait_invite_transfert',
            field=models.BooleanField(default=False, verbose_name='2 transferts a\xe9roport et h\xf4tel (seulement si votre accompagnateur voyage avec vous)'),
        ),
        migrations.AddField(
            model_name='inscription',
            name='programmation_soiree_10_mai',
            field=models.BooleanField(default=False, verbose_name='Je participerai \xe0 la soir\xe9e du 10 mai.'),
        ),
        migrations.AddField(
            model_name='inscription',
            name='programmation_soiree_10_mai_invite',
            field=models.BooleanField(default=False, verbose_name='D\xeener du 10 mai'),
        ),
        migrations.AddField(
            model_name='inscription',
            name='programmation_soiree_9_mai',
            field=models.BooleanField(default=False, verbose_name='Je participerai \xe0 la soir\xe9e du 9 mai.'),
        ),
        migrations.AddField(
            model_name='inscription',
            name='programmation_soiree_9_mai_invite',
            field=models.BooleanField(default=False, verbose_name='D\xeener du 9 mai'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala',
            field=models.BooleanField(default=False, verbose_name="Je participerai \xe0 la soir\xe9e de gala de cl\xf4ture de l'assembl\xe9e g\xe9n\xe9rale le 11 mai"),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala_invite',
            field=models.BooleanField(default=False, verbose_name='D\xeener de gala du 11 mai'),
        ),
    ]
