# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import ag.gestion.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0007_implantation'),
        ('gestion', '0004_auto_20161017_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today)),
                ('montant_euros', models.DecimalField(verbose_name='Montant (\u20ac)', max_digits=10, decimal_places=2)),
                ('moyen', models.CharField(max_length=2, verbose_name='modalit\xe9', choices=[(b'CB', 'Carte bancaire'), (b'VB', 'Virement bancaire'), (b'CE', 'Ch\xe8que en euros'), (b'DL', 'Devises locales')])),
                ('ref', models.CharField(max_length=255, verbose_name='r\xe9f\xe9rence')),
                ('montant_devise_locale', models.DecimalField(null=True, verbose_name='paiement en devises locales', max_digits=16, decimal_places=2, blank=True)),
                ('devise_locale', models.CharField(max_length=3, null=True, verbose_name='devise paiement', blank=True)),
                ('implantation', models.ForeignKey(to='reference.Implantation')),
            ],
        ),
        migrations.RemoveField(
            model_name='activite',
            name='prix',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='paiement',
        ),
        migrations.AlterField(
            model_name='fichier',
            name='fichier',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location=b'/media/benselme/data/dev/projects/auf/ag2017_auf_org/medias_participants'), upload_to=ag.gestion.models.get_participant_file_path),
        ),
        migrations.AddField(
            model_name='paiement',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
    ]
