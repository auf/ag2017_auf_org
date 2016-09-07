# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0003_inscription_type_chambre_hotel'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaypalInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tx_id', models.UUIDField(default=uuid.uuid4, db_index=True)),
                ('montant', models.DecimalField(max_digits=6, decimal_places=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaypalResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_reponse', models.CharField(max_length=3, choices=[(b'IPN', 'Instant Payment Notification'), (b'PDT', 'Payment Data Transfer')])),
                ('date_heure', models.DateTimeField(null=True, verbose_name='Date et heure du paiement')),
                ('montant', models.DecimalField(null=True, max_digits=6, decimal_places=2)),
                ('devise', models.CharField(max_length=32, null=True)),
                ('tx_id', models.CharField(max_length=250, db_index=True)),
                ('statut', models.CharField(max_length=64, null=True)),
                ('raison_attente', models.CharField(max_length=128, null=True)),
                ('request_data', models.TextField(null=True)),
                ('validation_response_data', models.TextField(null=True)),
                ('validated', models.BooleanField(default=False)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='paiementpaypal',
            name='inscription',
        ),
        migrations.AlterField(
            model_name='inscription',
            name='type_chambre_hotel',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'1', b'chambre avec 1 lit simple'), (b'2', b'chambre double (suppl\xc3\xa9ment de 100\xe2\x82\xac)')]),
        ),
        migrations.DeleteModel(
            name='PaiementPaypal',
        ),
        migrations.AddField(
            model_name='paypalresponse',
            name='inscription',
            field=models.ForeignKey(to='inscription.Inscription', null=True),
        ),
    ]
