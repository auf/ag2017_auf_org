# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import auf.django.mailing.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '__first__'),
        ('reference', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forfait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('montant', models.IntegerField()),
                ('categorie', models.CharField(max_length=4, choices=[(b'insc', 'Inscription'), (b'invi', 'Invit\xe9'), (b'hebe', 'H\xe9bergement')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('genre', models.CharField(blank=True, max_length=1, verbose_name=b'civilit\xc3\xa9', choices=[(b'M', 'M.'), (b'F', 'Mme')])),
                ('nom', models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'nom')),
                ('prenom', models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'pr\xc3\xa9nom(s)')),
                ('nationalite', models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'nationalit\xc3\xa9', blank=True)),
                ('date_naissance', models.DateField(help_text='format: jj/mm/aaaa', null=True, verbose_name=b'   Date de naissance', blank=True)),
                ('poste', models.CharField(max_length=100, verbose_name=b'poste occup\xc3\xa9', blank=True)),
                ('courriel', models.EmailField(max_length=254, blank=True)),
                ('adresse', models.TextField(help_text="Ceci est l'adresse de votre \xe9tablissement. Modifiez ces donn\xe9es pour changer l'adresse de facturation.", verbose_name=b'Adresse de facturation', blank=True)),
                ('ville', models.CharField(max_length=100, blank=True)),
                ('pays', models.CharField(max_length=100, blank=True)),
                ('code_postal', models.CharField(max_length=20, blank=True)),
                ('telephone', models.CharField(max_length=50, verbose_name=b't\xc3\xa9l\xc3\xa9phone', blank=True)),
                ('telecopieur', models.CharField(max_length=50, verbose_name=b't\xc3\xa9l\xc3\xa9copieur', blank=True)),
                ('date_arrivee_hotel', models.DateField(null=True, verbose_name="Date d'arriv\xe9e", blank=True)),
                ('date_depart_hotel', models.DateField(null=True, verbose_name='Date de d\xe9part', blank=True)),
                ('atteste_pha', models.CharField(max_length=1, null=True, choices=[(b'P', "J'atteste \xeatre la plus haute autorit\xe9 de mon \xe9tablissement et participerai \xe0 la 17\xe8me Assembl\xe9e g\xe9n\xe9rale de l'AUF"), (b'R', "J'atteste \xeatre le repr\xe9sentant d\xfbment mandat\xe9 par la plus haute autorit\xe9 de mon \xe9tablissement pour participer \xe0 la 17\xe8me Assembl\xe9e g\xe9n\xe9rale de l'AUF")])),
                ('identite_accompagnateur_confirmee', models.BooleanField(default=False, verbose_name=b'identit\xc3\xa9 confirm\xc3\xa9e')),
                ('conditions_acceptees', models.BooleanField(default=False, verbose_name='J\'ai lu et j\'accepte les <a href="/inscription/conditions-generales/" onclick="javascript:window.open(\'/inscription/conditions-generales/\');return false;" target="_blank">conditions g\xe9n\xe9rales d\'inscription</a>')),
                ('accompagnateur', models.BooleanField(default=False, verbose_name="Je serai accompagn\xe9(e) par une autre personne qui ne participera pas \xe0 l'assembl\xe9e g\xe9n\xe9rale")),
                ('accompagnateur_genre', models.CharField(blank=True, max_length=1, verbose_name='genre', choices=[(b'M', 'M.'), (b'F', 'Mme')])),
                ('accompagnateur_nom', models.CharField(max_length=100, verbose_name=b'nom', blank=True)),
                ('accompagnateur_prenom', models.CharField(max_length=100, verbose_name='pr\xe9nom(s)', blank=True)),
                ('programmation_soiree_9_mai', models.BooleanField(default=False, verbose_name='D\xeener du 9 mai \xe0 l\u2019h\xf4tel Mogador')),
                ('programmation_soiree_9_mai_invite', models.BooleanField(default=False, verbose_name='D\xeener du 9 mai \xe0 l\u2019h\xf4tel Mogador')),
                ('programmation_soiree_10_mai', models.BooleanField(default=False, verbose_name='Soir\xe9e Fantasia "Chez Ali" du 10 mai.')),
                ('programmation_soiree_10_mai_invite', models.BooleanField(default=False, verbose_name='Soir\xe9e Fantasia "Chez Ali" du 10 mai.')),
                ('programmation_gala', models.BooleanField(default=False, verbose_name="Soir\xe9e de gala de cl\xf4ture de l'Assembl\xe9e g\xe9n\xe9rale le 11 mai.")),
                ('programmation_gala_invite', models.BooleanField(default=False, verbose_name="Soir\xe9e de gala de cl\xf4ture de l'Assembl\xe9e g\xe9n\xe9rale le 11 mai.")),
                ('programmation_soiree_12_mai', models.BooleanField(default=False, verbose_name='Cocktail d\xeenatoire de cl\xf4ture le 12 mai.')),
                ('forfait_invite_dejeuners', models.BooleanField(default=False, verbose_name='Forfait 3 D\xe9jeuners (9,10 et 11)')),
                ('forfait_invite_transfert', models.BooleanField(default=False, verbose_name='2 transferts a\xe9roport et h\xf4tel (seulement si votre accompagnateur voyage avec vous)')),
                ('prise_en_charge_hebergement', models.NullBooleanField(verbose_name=b'Je demande la prise en charge de mon h\xc3\xa9bergement.')),
                ('prise_en_charge_transport', models.NullBooleanField(verbose_name=b'Je demande la prise en charge de mon transport.')),
                ('arrivee_date', models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b"date d'arriv\xc3\xa9e \xc3\xa0 S\xc3\xa3o Paulo", blank=True)),
                ('arrivee_heure', models.TimeField(help_text=b'format: hh:mm', null=True, verbose_name=b'heure', blank=True)),
                ('arrivee_compagnie', models.CharField(max_length=100, verbose_name=b'compagnie', blank=True)),
                ('arrivee_vol', models.CharField(max_length=100, verbose_name=b'vol', blank=True)),
                ('depart_de', models.CharField(blank=True, max_length=10, verbose_name=b'd\xc3\xa9part de', choices=[(b'sao-paulo', 'S\xe3o Paulo'), (b'rio', 'Rio de Janeiro')])),
                ('depart_date', models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b'date de d\xc3\xa9part de S\xc3\xa3o Paulo', blank=True)),
                ('depart_heure', models.TimeField(help_text=b'format: hh:mm', null=True, verbose_name=b'heure', blank=True)),
                ('depart_compagnie', models.CharField(max_length=100, verbose_name=b'compagnie', blank=True)),
                ('depart_vol', models.CharField(max_length=100, verbose_name=b'vol', blank=True)),
                ('fermee', models.BooleanField(default=False, verbose_name='Confirm\xe9e par le participant')),
                ('date_fermeture', models.DateField(null=True, verbose_name='Confirm\xe9e le')),
                ('numero_dossier', models.CharField(max_length=8, unique=True, null=True)),
                ('reseautage', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pour_mandate', models.BooleanField(default=False)),
                ('courriel', models.EmailField(max_length=254, null=True)),
                ('jeton', models.CharField(default=auf.django.mailing.models.generer_jeton, max_length=32)),
                ('nom', models.CharField(max_length=100, null=True)),
                ('prenom', models.CharField(max_length=100, null=True)),
                ('etablissement', models.ForeignKey(to='reference.Etablissement')),
            ],
        ),
        migrations.CreateModel(
            name='InvitationEnveloppe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enveloppe', models.OneToOneField(to='mailing.Enveloppe')),
                ('invitation', models.ForeignKey(to='inscription.Invitation')),
            ],
        ),
        migrations.CreateModel(
            name='PaypalInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invoice_uid', models.UUIDField(default=uuid.uuid4, db_index=True)),
                ('montant', models.DecimalField(max_digits=6, decimal_places=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('inscription', models.ForeignKey(to='inscription.Inscription')),
            ],
        ),
        migrations.CreateModel(
            name='PaypalResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_reponse', models.CharField(max_length=3, choices=[(b'IPN', 'Instant Payment Notification'), (b'PDT', 'Payment Data Transfer'), (b'CAN', 'Cancelled')])),
                ('date_heure', models.DateTimeField(null=True, verbose_name='Date et heure du paiement')),
                ('montant', models.DecimalField(null=True, max_digits=6, decimal_places=2)),
                ('devise', models.CharField(max_length=32, null=True)),
                ('invoice_uid', models.UUIDField(null=True, db_index=True)),
                ('txn_id', models.CharField(max_length=250, null=True, db_index=True)),
                ('statut', models.CharField(max_length=64, null=True)),
                ('raison_attente', models.CharField(max_length=128, null=True)),
                ('request_data', models.TextField(null=True)),
                ('validation_response_data', models.TextField(null=True)),
                ('validated', models.BooleanField(default=False)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('inscription', models.ForeignKey(to='inscription.Inscription', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='inscription',
            name='invitation',
            field=models.OneToOneField(to='inscription.Invitation'),
        ),
    ]
