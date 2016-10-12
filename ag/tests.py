# -*- encoding: utf-8 -*-
import datetime
from ag.core.test_utils import RegionFactory, PaysFactory, EtablissementFactory
from ag.gestion import montants
from ag.gestion.models import AGRole, ROLE_ADMIN, StatutParticipant, TypeInstitutionSupplementaire, Participant, \
    Activite
from auf.django.mailing.models import ModeleCourriel
from ag.reference.models import Pays, Region, Etablissement
from django.contrib.auth.models import User


def create_fixtures(test_case):
    test_case.user = User.objects.create_user('john', 'lennon@thebeatles.com',
                                              'johnpassword')
    test_case.user.roles.add(AGRole(type_role=ROLE_ADMIN))
    test_case.user.is_staff = True
    test_case.user.save()

    region = RegionFactory()
    test_case.region = region

    test_case.pays_sud = pays = PaysFactory(code='TS', sud=True)
    test_case.pays_nord = pays_nord = PaysFactory(code='NN', sud=False)

    etablissement = EtablissementFactory(
        pays=pays,
        responsable_courriel='abc@test.org',
        membre=True,
        qualite='ESR',
        statut='T',
        region=region
    )
    test_case.etablissement_id = etablissement.id

    etablissement_nord = EtablissementFactory(
        pays=pays_nord, membre=True, responsable_courriel='nord@test.org',
        statut='T')
    test_case.etablissement_nord_id = etablissement_nord.id

    etablissement_sud_associe = EtablissementFactory(
        pays=pays, membre=True, responsable_courriel='sud_assoc@test.org',
        qualite='ESR', statut='A')
    test_case.etablissement_sud_associe_id = etablissement_sud_associe.id

    etablissement_non_membre = EtablissementFactory(
        pays=pays_nord, membre=False, responsable_courriel='nord@test.org')
    test_case.etablissement_non_membre_id = etablissement_non_membre.id

    etablissement_sans_courriel = EtablissementFactory(
        membre=True, responsable_courriel='', pays=pays_nord)
    test_case.etablissement_pas_de_courriel_id = etablissement_sans_courriel.id

    test_case.total_etablissements_membres_avec_courriel = 3

    modele_courriel_mandate = make_modele_courriel_mandate()
    test_case.modele_courriel_mandate = modele_courriel_mandate

    modele_courriel_mandate_rappel = ModeleCourriel()
    modele_courriel_mandate_rappel.sujet = 'test rappel mand'
    modele_courriel_mandate_rappel.code = 'mand_rel'
    modele_courriel_mandate_rappel.corps = 'Rappel {{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_mandate_rappel.html = False
    modele_courriel_mandate_rappel.save()
    test_case.modele_courriel_mandate_rappel = modele_courriel_mandate_rappel

    modele_courriel_accompagnateur = ModeleCourriel()
    modele_courriel_accompagnateur.sujet = 'test accompagnateur'
    modele_courriel_accompagnateur.code = 'acc'
    modele_courriel_accompagnateur.corps = '{{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_accompagnateur.html = False
    modele_courriel_accompagnateur.save()
    test_case.modele_courriel_accompagnateur = modele_courriel_mandate

    modele_courriel_rappel = ModeleCourriel()
    modele_courriel_rappel.sujet = 'test rappel'
    modele_courriel_rappel.code = 'rappel'
    modele_courriel_rappel.corps = '{{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}'
    modele_courriel_rappel.html = False
    modele_courriel_rappel.save()

    for code_activite, (_, _) in montants.CODES_MONTANTS_ACTIVITES:
        Activite.objects.create(code=code_activite, libelle=code_activite,
                                prix=0, prix_invite=30)


def make_modele_courriel_mandate():
    return ModeleCourriel.objects.create(
        sujet='test', code='mand',
        corps='{{ nom_destinataire }}-{{ nom_etablissement }}-{{ url }}',
        html=False,
    )


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