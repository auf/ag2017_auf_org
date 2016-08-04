# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='accompagnateur',
            field=models.BooleanField(default=False, verbose_name="Je serai accompagn\xe9(e) par une autre personne qui ne participera pas \xe0 l'assembl\xe9e g\xe9n\xe9rale"),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='conditions_acceptees',
            field=models.BooleanField(default=False, verbose_name='J\'ai lu et j\'accepte les <a href="/inscription/conditions-generales/" onclick="javascript:window.open(\'/inscription/conditions-generales/\');return false;" target="_blank">conditions g\xe9n\xe9rales d\'inscription</a>'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='identite_confirmee',
            field=models.BooleanField(default=False, verbose_name=b'identit\xc3\xa9 confirm\xc3\xa9e'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala',
            field=models.BooleanField(default=False, verbose_name="Je participerai \xe0 la soir\xe9e de gala de cl\xf4ture de l'assembl\xe9e g\xe9n\xe9rale le 9 mai 2013."),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala_invite',
            field=models.BooleanField(default=False, verbose_name='Mon invit\xe9 \xe9galement.'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_interconsulaire',
            field=models.BooleanField(default=False, verbose_name='Je participerai \xe0 la soir\xe9e interconsulaire le 8 mai 2013.'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_interconsulaire_invite',
            field=models.BooleanField(default=False, verbose_name='Mon invit\xe9 \xe9galement.'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_unesp',
            field=models.BooleanField(default=False, verbose_name="Je participerai \xe0 la soir\xe9e organis\xe9e par l'UNESP le 7 mai 2013."),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_unesp_invite',
            field=models.BooleanField(default=False, verbose_name='Mon invit\xe9 \xe9galement.'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='pour_mandate',
            field=models.BooleanField(default=False),
        ),
    ]
