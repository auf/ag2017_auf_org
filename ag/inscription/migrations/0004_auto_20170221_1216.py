# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0003_auto_20170109_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='arrivee_a',
            field=models.CharField(blank=True, max_length=10, verbose_name=b'arriv\xc3\xa9e \xc3\xa0', choices=[(b'marrakech', 'Marrakech'), (b'casa', 'Casablanca')]),
        ),
        migrations.AddField(
            model_name='inscription',
            name='arrivee_compagnie',
            field=models.CharField(max_length=64, null=True, verbose_name=b'compagnie', blank=True),
        ),
        migrations.AddField(
            model_name='inscription',
            name='depart_compagnie',
            field=models.CharField(max_length=64, null=True, verbose_name=b'compagnie', blank=True),
        ),
    ]
