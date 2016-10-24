# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0015_auto_20161019_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='programmation_soiree_12_mai',
            field=models.BooleanField(default=False, verbose_name='Cocktail d\xeenatoire de cl\xf4ture le 12 mai.'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala',
            field=models.BooleanField(default=False, verbose_name="Soir\xe9e de gala de cl\xf4ture de l'Assembl\xe9e g\xe9n\xe9rale le 11 mai."),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala_invite',
            field=models.BooleanField(default=False, verbose_name="Soir\xe9e de gala de cl\xf4ture de l'Assembl\xe9e g\xe9n\xe9rale le 11 mai."),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_10_mai',
            field=models.BooleanField(default=False, verbose_name='Soir\xe9e Fantasia "Chez Ali" du 10 mai.'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_10_mai_invite',
            field=models.BooleanField(default=False, verbose_name='Soir\xe9e Fantasia "Chez Ali" du 10 mai.'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_9_mai',
            field=models.BooleanField(default=False, verbose_name='D\xeener du 9 mai \xe0 l\u2019h\xf4tel Mogador'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_soiree_9_mai_invite',
            field=models.BooleanField(default=False, verbose_name='D\xeener du 9 mai \xe0 l\u2019h\xf4tel Mogador'),
        ),
    ]
