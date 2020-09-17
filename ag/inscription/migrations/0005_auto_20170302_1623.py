# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0004_auto_20170221_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='arrivee_a',
            field=models.CharField(blank=True, max_length=10, verbose_name=b'arriv\xc3\xa9e \xc3\xa0', choices=[(b'Marrakech', 'Marrakech'), (b'Casablanca', 'Casablanca')]),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='depart_date',
            field=models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b'date de d\xc3\xa9part', blank=True),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='depart_de',
            field=models.CharField(blank=True, max_length=10, verbose_name=b'd\xc3\xa9part de', choices=[(b'Marrakech', 'Marrakech'), (b'Casablanca', 'Casablanca')]),
        ),
    ]
