# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0002_auto_20161116_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='arrivee_date',
            field=models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b"date d'arriv\xc3\xa9e \xc3\xa0 Marrakech", blank=True),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='conditions_acceptees',
            field=models.BooleanField(default=False, verbose_name='J\'ai lu et j\'accepte les <a href="https://ag2017.auf.org/media/filer_public/7f/00/7f003ea6-7fa6-44f6-a992-14bcd5acf654/auf_conditions_inscritpion_ag2017.pdf" onclick="javascript:window.open(\'https://ag2017.auf.org/media/filer_public/7f/00/7f003ea6-7fa6-44f6-a992-14bcd5acf654/auf_conditions_inscritpion_ag2017.pdf\');return false;" target="_blank">conditions g\xe9n\xe9rales d\'inscription</a>'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='depart_date',
            field=models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b'date de d\xc3\xa9part de Marrakech', blank=True),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='depart_de',
            field=models.CharField(blank=True, max_length=10, verbose_name=b'd\xc3\xa9part de', choices=[(b'marrakech', 'Marrakech'), (b'casa', 'Casablanca')]),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala',
            field=models.BooleanField(default=False, verbose_name="Soir\xe9e de gala de l'Assembl\xe9e g\xe9n\xe9rale le 11 mai."),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='programmation_gala_invite',
            field=models.BooleanField(default=False, verbose_name="Soir\xe9e de gala de l'Assembl\xe9e g\xe9n\xe9rale le 11 mai."),
        ),
    ]
