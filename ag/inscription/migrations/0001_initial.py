# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Invitation'
        db.create_table('inscription_invitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('etablissement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['references.Etablissement'])),
            ('pour_mandate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('courriel', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('jeton', self.gf('django.db.models.fields.CharField')(default='SaMUEG3oUpPCwQY3qSTZfngNnrlSncN8', max_length=32)),
        ))
        db.send_create_signal('inscription', ['Invitation'])

        # Adding model 'InvitationEnveloppe'
        db.create_table('inscription_invitationenveloppe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enveloppe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mailing.Enveloppe'], unique=True)),
            ('invitation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inscription.Invitation'])),
        ))
        db.send_create_signal('inscription', ['InvitationEnveloppe'])

        # Adding model 'Inscription'
        db.create_table('inscription_inscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('prenom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('nationalite', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('date_naissance', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('poste', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('courriel', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('adresse', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ville', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('pays', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('code_postal', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('telecopieur', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('date_arrivee_hotel', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_depart_hotel', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('paiement', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('invitation', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['inscription.Invitation'], unique=True)),
            ('identite_confirmee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('conditions_acceptees', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accompagnateur', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accompagnateur_genre', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('accompagnateur_nom', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('accompagnateur_prenom', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('programmation_soiree_unesp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('programmation_soiree_unesp_invite', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('programmation_soiree_interconsulaire', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('programmation_soiree_interconsulaire_invite', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('programmation_gala', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('programmation_gala_invite', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prise_en_charge_hebergement', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('prise_en_charge_transport', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('arrivee_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('arrivee_heure', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('arrivee_compagnie', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('arrivee_vol', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('depart_de', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('depart_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('depart_heure', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('depart_compagnie', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('depart_vol', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('type_chambre_hotel', self.gf('django.db.models.fields.CharField')(default='S', max_length=1)),
            ('demande_chambre', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fermee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_fermeture', self.gf('django.db.models.fields.DateField')(null=True)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('inscription', ['Inscription'])

        # Adding model 'PaiementPaypal'
        db.create_table('inscription_paiementpaypal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_heure', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('montant', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('devise', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('numero_transaction', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250, db_index=True)),
            ('statut', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('raison_attente', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('ipn_post_data', self.gf('django.db.models.fields.TextField')(null=True)),
            ('pdt_reponse', self.gf('django.db.models.fields.TextField')(null=True)),
            ('inscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inscription.Inscription'], null=True)),
            ('ipn_valide', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pdt_valide', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('inscription', ['PaiementPaypal'])

    def backwards(self, orm):
        # Deleting model 'Invitation'
        db.delete_table('inscription_invitation')

        # Deleting model 'InvitationEnveloppe'
        db.delete_table('inscription_invitationenveloppe')

        # Deleting model 'Inscription'
        db.delete_table('inscription_inscription')

        # Deleting model 'PaiementPaypal'
        db.delete_table('inscription_paiementpaypal')

    models = {
        'inscription.inscription': {
            'Meta': {'object_name': 'Inscription'},
            'accompagnateur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'accompagnateur_genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'accompagnateur_nom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'accompagnateur_prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'adresse': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'arrivee_compagnie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'arrivee_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'arrivee_heure': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'arrivee_vol': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'conditions_acceptees': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_arrivee_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_depart_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_fermeture': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_naissance': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'demande_chambre': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'depart_compagnie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'depart_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'depart_de': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'depart_heure': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'depart_vol': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fermee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identite_confirmee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invitation': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['inscription.Invitation']", 'unique': 'True'}),
            'nationalite': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'paiement': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'pays': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'poste': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'prise_en_charge_hebergement': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'prise_en_charge_transport': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'programmation_gala': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_gala_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_interconsulaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_interconsulaire_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_unesp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_unesp_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'telecopieur': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type_chambre_hotel': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'inscription.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'etablissement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Etablissement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jeton': ('django.db.models.fields.CharField', [], {'default': "'P0bSZ3Cn0AlOq3vCuJEs7CxnWp1MrZsd'", 'max_length': '32'}),
            'pour_mandate': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'inscription.invitationenveloppe': {
            'Meta': {'object_name': 'InvitationEnveloppe'},
            'enveloppe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mailing.Enveloppe']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inscription.Invitation']"})
        },
        'inscription.paiementpaypal': {
            'Meta': {'object_name': 'PaiementPaypal'},
            'date_heure': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'devise': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inscription.Inscription']", 'null': 'True'}),
            'ipn_post_data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ipn_valide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'montant': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'numero_transaction': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'}),
            'pdt_reponse': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'pdt_valide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'raison_attente': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'statut': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'})
        },
        'mailing.enveloppe': {
            'Meta': {'object_name': 'Enveloppe'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modele': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mailing.ModeleCourriel']"})
        },
        'mailing.modelecourriel': {
            'Meta': {'object_name': 'ModeleCourriel'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8'}),
            'corps': ('django.db.models.fields.TextField', [], {}),
            'html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sujet': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'references.bureau': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Bureau', 'db_table': "u'ref_bureau'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implantation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Implantation']", 'db_column': "'implantation'"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nom_court': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nom_long': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'db_column': "'region'"})
        },
        'references.etablissement': {
            'Meta': {'ordering': "['pays__nom', 'nom']", 'object_name': 'Etablissement', 'db_table': "u'ref_etablissement'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'adresse': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cedex': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'commentaire': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_modification': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'historique': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implantation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'db_column': "'implantation'", 'to': "orm['references.Implantation']"}),
            'membre': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'membre_adhesion_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pays': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to_field': "'code'", 'db_column': "'pays'", 'to': "orm['references.Pays']"}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'qualite': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'db_column': "'region'", 'to': "orm['references.Region']"}),
            'responsable_courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'responsable_fonction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'responsable_genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'responsable_nom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'responsable_prenom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sigle': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'statut': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'references.implantation': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Implantation', 'db_table': "u'ref_implantation'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'adresse_physique_bureau': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_code_postal': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'adresse_physique_code_postal_avant_ville': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'adresse_physique_no': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'adresse_physique_pays': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'impl_adresse_physique'", 'to_field': "'code'", 'db_column': "'adresse_physique_pays'", 'to': "orm['references.Pays']"}),
            'adresse_physique_precision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_precision_avant': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_rue': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_ville': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'adresse_postale_boite_postale': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_bureau': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_code_postal_avant_ville': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'adresse_postale_no': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_pays': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'impl_adresse_postale'", 'to_field': "'code'", 'db_column': "'adresse_postale_pays'", 'to': "orm['references.Pays']"}),
            'adresse_postale_precision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_precision_avant': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_rue': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_ville': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'bureau_rattachement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Implantation']", 'db_column': "'bureau_rattachement'"}),
            'code_meteo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'commentaire': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'courriel_interne': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_extension': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_fermeture': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_inauguration': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_ouverture': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fax_interne': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fuseau_horaire': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'hebergement_convention': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'hebergement_convention_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hebergement_etablissement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modif_date': ('django.db.models.fields.DateField', [], {}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nom_court': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nom_long': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'db_column': "'region'"}),
            'remarque': ('django.db.models.fields.TextField', [], {}),
            'responsable_implantation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'statut': ('django.db.models.fields.IntegerField', [], {}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'telephone_interne': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'references.pays': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Pays', 'db_table': "u'ref_pays'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'code_bureau': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Bureau']", 'to_field': "'code'", 'null': 'True', 'db_column': "'code_bureau'", 'blank': 'True'}),
            'code_iso3': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'developpement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monnaie': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nord_sud': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'db_column': "'region'"})
        },
        'references.region': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Region', 'db_table': "u'ref_region'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implantation_bureau': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'gere_region'", 'null': 'True', 'db_column': "'implantation_bureau'", 'to': "orm['references.Implantation']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['inscription']