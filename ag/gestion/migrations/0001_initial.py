# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TypeInstitutionSupplementaire'
        db.create_table('gestion_typeinstitutionsupplementaire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ordre', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gestion', ['TypeInstitutionSupplementaire'])

        # Adding model 'StatutParticipant'
        db.create_table('gestion_statutparticipant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ordre', self.gf('django.db.models.fields.IntegerField')()),
            ('droit_de_vote', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('gestion', ['StatutParticipant'])

        # Adding model 'PointDeSuivi'
        db.create_table('gestion_pointdesuivi', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ordre', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gestion', ['PointDeSuivi'])

        # Adding model 'Hotel'
        db.create_table('gestion_hotel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('adresse', self.gf('django.db.models.fields.TextField')()),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('courriel', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('gestion', ['Hotel'])

        # Adding model 'Chambre'
        db.create_table('gestion_chambre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Hotel'])),
            ('type_chambre', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('places', self.gf('django.db.models.fields.IntegerField')()),
            ('nb_total', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('prix', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('gestion', ['Chambre'])

        # Adding unique constraint on 'Chambre', fields ['hotel', 'type_chambre']
        db.create_unique('gestion_chambre', ['hotel_id', 'type_chambre'])

        # Adding model 'TypeFrais'
        db.create_table('gestion_typefrais', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('gestion', ['TypeFrais'])

        # Adding model 'Activite'
        db.create_table('gestion_activite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('prix', self.gf('django.db.models.fields.FloatField')()),
            ('prix_invite', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('gestion', ['Activite'])

        # Adding model 'Probleme'
        db.create_table('gestion_probleme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('libelle', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('severite', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gestion', ['Probleme'])

        # Adding model 'ParticipationActivite'
        db.create_table('gestion_participationactivite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Activite'])),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Participant'])),
            ('avec_invites', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('gestion', ['ParticipationActivite'])

        # Adding unique constraint on 'ParticipationActivite', fields ['activite', 'participant']
        db.create_unique('gestion_participationactivite', ['activite_id', 'participant_id'])

        # Adding model 'Participant'
        db.create_table('gestion_participant', (
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
            ('inscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inscription.Inscription'], null=True)),
            ('utiliser_adresse_gde', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('statut', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.StatutParticipant'])),
            ('notes_statut', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('desactive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type_institution', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('instance_auf', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('type_autre_institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.TypeInstitutionSupplementaire'], null=True)),
            ('nom_autre_institution', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('etablissement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['references.Etablissement'], null=True)),
            ('accompte', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
            ('numero_facture', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('date_facturation', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('facturation_validee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes_facturation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('prise_en_charge_inscription', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prise_en_charge_transport', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prise_en_charge_sejour', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prise_en_charge_activites', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mode_paiement', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('imputation', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('modalite_versement_frais_sejour', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('transport_organise_par_auf', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('statut_dossier_transport', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('modalite_retrait_billet', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('numero_dossier_transport', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('notes_transport', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('remarques_transport', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('reservation_hotel_par_auf', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes_hebergement', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Hotel'], null=True)),
        ))
        db.send_create_signal('gestion', ['Participant'])

        # Adding M2M table for field suivi on 'Participant'
        db.create_table('gestion_participant_suivi', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('participant', models.ForeignKey(orm['gestion.participant'], null=False)),
            ('pointdesuivi', models.ForeignKey(orm['gestion.pointdesuivi'], null=False))
        ))
        db.create_unique('gestion_participant_suivi', ['participant_id', 'pointdesuivi_id'])

        # Adding M2M table for field problemes on 'Participant'
        db.create_table('gestion_participant_problemes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('participant', models.ForeignKey(orm['gestion.participant'], null=False)),
            ('probleme', models.ForeignKey(orm['gestion.probleme'], null=False))
        ))
        db.create_unique('gestion_participant_problemes', ['participant_id', 'probleme_id'])

        # Adding model 'Invite'
        db.create_table('gestion_invite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('prenom', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Participant'])),
        ))
        db.send_create_signal('gestion', ['Invite'])

        # Adding model 'ReservationChambre'
        db.create_table('gestion_reservationchambre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Participant'])),
            ('type_chambre', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('nombre', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gestion', ['ReservationChambre'])

        # Adding unique constraint on 'ReservationChambre', fields ['participant', 'type_chambre']
        db.create_unique('gestion_reservationchambre', ['participant_id', 'type_chambre'])

        # Adding model 'InfosVol'
        db.create_table('gestion_infosvol', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Participant'])),
            ('ville_depart', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('date_depart', self.gf('django.db.models.fields.DateField')(null=True)),
            ('heure_depart', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('ville_arrivee', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('date_arrivee', self.gf('django.db.models.fields.DateField')(null=True)),
            ('heure_arrivee', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('numero_vol', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('compagnie', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('prix', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('type_infos', self.gf('django.db.models.fields.IntegerField')(default=2)),
        ))
        db.send_create_signal('gestion', ['InfosVol'])

        # Adding model 'Frais'
        db.create_table('gestion_frais', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Participant'])),
            ('type_frais', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.TypeFrais'])),
            ('montant', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('gestion', ['Frais'])

        # Adding model 'Fichier'
        db.create_table('gestion_fichier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gestion.Participant'])),
            ('fichier', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('cree_le', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('gestion', ['Fichier'])

    def backwards(self, orm):
        # Removing unique constraint on 'ReservationChambre', fields ['participant', 'type_chambre']
        db.delete_unique('gestion_reservationchambre', ['participant_id', 'type_chambre'])

        # Removing unique constraint on 'ParticipationActivite', fields ['activite', 'participant']
        db.delete_unique('gestion_participationactivite', ['activite_id', 'participant_id'])

        # Removing unique constraint on 'Chambre', fields ['hotel', 'type_chambre']
        db.delete_unique('gestion_chambre', ['hotel_id', 'type_chambre'])

        # Deleting model 'TypeInstitutionSupplementaire'
        db.delete_table('gestion_typeinstitutionsupplementaire')

        # Deleting model 'StatutParticipant'
        db.delete_table('gestion_statutparticipant')

        # Deleting model 'PointDeSuivi'
        db.delete_table('gestion_pointdesuivi')

        # Deleting model 'Hotel'
        db.delete_table('gestion_hotel')

        # Deleting model 'Chambre'
        db.delete_table('gestion_chambre')

        # Deleting model 'TypeFrais'
        db.delete_table('gestion_typefrais')

        # Deleting model 'Activite'
        db.delete_table('gestion_activite')

        # Deleting model 'Probleme'
        db.delete_table('gestion_probleme')

        # Deleting model 'ParticipationActivite'
        db.delete_table('gestion_participationactivite')

        # Deleting model 'Participant'
        db.delete_table('gestion_participant')

        # Removing M2M table for field suivi on 'Participant'
        db.delete_table('gestion_participant_suivi')

        # Removing M2M table for field problemes on 'Participant'
        db.delete_table('gestion_participant_problemes')

        # Deleting model 'Invite'
        db.delete_table('gestion_invite')

        # Deleting model 'ReservationChambre'
        db.delete_table('gestion_reservationchambre')

        # Deleting model 'InfosVol'
        db.delete_table('gestion_infosvol')

        # Deleting model 'Frais'
        db.delete_table('gestion_frais')

        # Deleting model 'Fichier'
        db.delete_table('gestion_fichier')

    models = {
        'gestion.activite': {
            'Meta': {'object_name': 'Activite'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'prix': ('django.db.models.fields.FloatField', [], {}),
            'prix_invite': ('django.db.models.fields.FloatField', [], {})
        },
        'gestion.chambre': {
            'Meta': {'unique_together': "(('hotel', 'type_chambre'),)", 'object_name': 'Chambre'},
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb_total': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'places': ('django.db.models.fields.IntegerField', [], {}),
            'prix': ('django.db.models.fields.FloatField', [], {}),
            'type_chambre': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'gestion.fichier': {
            'Meta': {'object_name': 'Fichier'},
            'cree_le': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fichier': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"})
        },
        'gestion.frais': {
            'Meta': {'object_name': 'Frais'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': ('django.db.models.fields.FloatField', [], {}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'type_frais': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.TypeFrais']"})
        },
        'gestion.hotel': {
            'Meta': {'object_name': 'Hotel'},
            'adresse': ('django.db.models.fields.TextField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'gestion.infosvol': {
            'Meta': {'ordering': "['date_depart', 'heure_depart']", 'object_name': 'InfosVol'},
            'compagnie': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'date_arrivee': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_depart': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'heure_arrivee': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'heure_depart': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numero_vol': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'prix': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'type_infos': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'ville_arrivee': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'ville_depart': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'gestion.invite': {
            'Meta': {'object_name': 'Invite'},
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gestion.participant': {
            'Meta': {'object_name': 'Participant'},
            'accompte': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'activites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gestion.Activite']", 'through': "orm['gestion.ParticipationActivite']", 'symmetrical': 'False'}),
            'adresse': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_arrivee_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_depart_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_facturation': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_naissance': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'desactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'etablissement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Etablissement']", 'null': 'True'}),
            'facturation_validee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Hotel']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imputation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'inscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inscription.Inscription']", 'null': 'True'}),
            'instance_auf': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'modalite_retrait_billet': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'modalite_versement_frais_sejour': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'mode_paiement': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'nationalite': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'nom_autre_institution': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_facturation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_hebergement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_statut': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_transport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'numero_dossier_transport': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'numero_facture': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'paiement': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'pays': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'poste': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'prise_en_charge_activites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prise_en_charge_inscription': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prise_en_charge_sejour': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prise_en_charge_transport': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'problemes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gestion.Probleme']", 'symmetrical': 'False'}),
            'remarques_transport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reservation_hotel_par_auf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'statut': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.StatutParticipant']"}),
            'statut_dossier_transport': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'suivi': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gestion.PointDeSuivi']", 'symmetrical': 'False'}),
            'telecopieur': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'transport_organise_par_auf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type_autre_institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.TypeInstitutionSupplementaire']", 'null': 'True'}),
            'type_institution': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'utiliser_adresse_gde': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'gestion.participationactivite': {
            'Meta': {'unique_together': "(('activite', 'participant'),)", 'object_name': 'ParticipationActivite'},
            'activite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Activite']"}),
            'avec_invites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"})
        },
        'gestion.pointdesuivi': {
            'Meta': {'ordering': "['ordre']", 'object_name': 'PointDeSuivi'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordre': ('django.db.models.fields.IntegerField', [], {})
        },
        'gestion.probleme': {
            'Meta': {'object_name': 'Probleme'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'severite': ('django.db.models.fields.IntegerField', [], {})
        },
        'gestion.reservationchambre': {
            'Meta': {'unique_together': "(('participant', 'type_chambre'),)", 'object_name': 'ReservationChambre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.IntegerField', [], {}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'type_chambre': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'gestion.statutparticipant': {
            'Meta': {'ordering': "['ordre']", 'object_name': 'StatutParticipant'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'droit_de_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordre': ('django.db.models.fields.IntegerField', [], {})
        },
        'gestion.typefrais': {
            'Meta': {'object_name': 'TypeFrais'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'gestion.typeinstitutionsupplementaire': {
            'Meta': {'ordering': "['ordre']", 'object_name': 'TypeInstitutionSupplementaire'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordre': ('django.db.models.fields.IntegerField', [], {})
        },
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
            'jeton': ('django.db.models.fields.CharField', [], {'default': "'dLIXhCPZIEc1SBJtEBkbLdUL5Q8iKj0U'", 'max_length': '32'}),
            'pour_mandate': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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

    complete_apps = ['gestion']