# -*- encoding: utf-8 -*-
import datetime
from ag.gestion.models import AGRole, ROLE_ADMIN, StatutParticipant, TypeInstitutionSupplementaire, Participant
from auf.django.mailing.models import ModeleCourriel
from auf.django.references.models import Pays, Region, Etablissement
from django.contrib.auth.models import User


def create_fixtures(test_case, do_login=True):
    test_case.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    test_case.user.roles.add(AGRole(type_role=ROLE_ADMIN))
    test_case.user.is_staff = True
    test_case.user.save()

    region = Region()
    region.actif = True
    region.nom = u'Région test'
    region.code = 'RTST'
    region.save()
    test_case.region = region

    pays = Pays()
    pays.region = region
    pays.nom = u'Pays test'
    pays.code = 'TS'
    pays.actif = True
    pays.nord_sud = 'Sud'
    pays.save()

    pays_nord = Pays()
    pays_nord.region = region
    pays_nord.nom = u'Pays test nord'
    pays_nord.code = 'NN'
    pays_nord.actif = True
    pays_nord.nord_sud = 'Nord'
    pays_nord.code_iso3 ='NN'
    pays_nord.save()

    etablissement = Etablissement()
    etablissement.nom = u'Établissement test'
    etablissement.pays = pays
    etablissement.responsable_courriel = 'abc@test.org'
    etablissement.membre = True
    etablissement.qualite = 'ESR'
    etablissement.statut = 'T'
    etablissement.region = region
    etablissement.save()
    test_case.etablissement_id = etablissement.id


    etablissement_nord = Etablissement()
    etablissement_nord.nom = u'Établissement test nord'
    etablissement_nord.pays = pays_nord
    etablissement_nord.membre = True
    etablissement_nord.responsable_courriel = 'nord@test.org'
    etablissement.statut = 'T'
    etablissement_nord.save()
    test_case.etablissement_nord_id = etablissement_nord.id

    etablissement_sud_associe = Etablissement()
    etablissement_sud_associe.nom = u'Établissement test sud associé'
    etablissement_sud_associe.pays = pays
    etablissement_sud_associe.membre = True
    etablissement_sud_associe.responsable_courriel = 'sud_assoc@test.org'
    etablissement_sud_associe.qualite = 'ESR'
    etablissement_sud_associe.statut = 'A'
    etablissement_sud_associe.save()
    test_case.etablissement_sud_associe_id = etablissement_sud_associe.id

    etablissement_non_membre = Etablissement()
    etablissement_non_membre.nom = u'Établissement test nord'
    etablissement_non_membre.pays = pays_nord
    etablissement_non_membre.membre = False
    etablissement_non_membre.responsable_courriel = 'nord@test.org'
    etablissement_non_membre.save()
    test_case.etablissement_non_membre_id = etablissement_non_membre.id


    etablissement_pas_de_courriel = Etablissement()
    etablissement_pas_de_courriel.nom = u'Établissement pas de courriel'
    etablissement_pas_de_courriel.pays = pays_nord
    etablissement_pas_de_courriel.membre = True
    etablissement_pas_de_courriel.responsable_courriel = ''
    etablissement_pas_de_courriel.save()
    test_case.etablissement_pas_de_courriel_id = etablissement_pas_de_courriel.id

    test_case.total_etablissements_membres_avec_courriel = 3

    modele_courriel_mandate = ModeleCourriel()
    modele_courriel_mandate.sujet = 'test'
    modele_courriel_mandate.code = 'mand'
    modele_courriel_mandate.corps = '{{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_mandate.save()
    test_case.modele_courriel_mandate = modele_courriel_mandate

    modele_courriel_mandate_rappel = ModeleCourriel()
    modele_courriel_mandate_rappel.sujet = 'test rappel mand'
    modele_courriel_mandate_rappel.code = 'mand_rel'
    modele_courriel_mandate_rappel.corps = 'Rappel {{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_mandate_rappel.save()
    test_case.modele_courriel_mandate_rappel = modele_courriel_mandate_rappel

    modele_courriel_accompagnateur = ModeleCourriel()
    modele_courriel_accompagnateur.sujet = 'test accompagnateur'
    modele_courriel_accompagnateur.code = 'acc'
    modele_courriel_accompagnateur.corps = '{{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_accompagnateur.save()
    test_case.modele_courriel_accompagnateur = modele_courriel_mandate

    modele_courriel_rappel = ModeleCourriel()
    modele_courriel_rappel.sujet = 'test rappel'
    modele_courriel_rappel.code = 'rappel'
    modele_courriel_rappel.corps = '{{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_rappel.save()

    if do_login:
        test_case.client.login(username='john', password='johnpassword')


def creer_participant(nom=None, prenom=None, code_statut='memb_inst',
                      code_type_autre_institution=None, **kwargs):
    defaults = {
        'nom': nom or u'Participant1',
        'prenom':  prenom or u'Test1',
        'adresse': u'adresse1',
        'code_postal': u'HHH 333',
        'courriel': u'adr.courriel@test.org',
        'date_naissance': datetime.date(1973, 07, 04),
        'statut': StatutParticipant.objects.get(code=code_statut),
        'type_institution': 'I',
        'instance_auf': 'A',
    }
    if code_type_autre_institution:
        type_autre_institution = TypeInstitutionSupplementaire.objects.get(
            code=code_type_autre_institution)
        defaults['type_autre_institution'] = type_autre_institution

    defaults.update(kwargs)
    participant = Participant(**defaults)
    participant.save()
    return participant