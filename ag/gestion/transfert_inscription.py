# -*- encoding: utf-8 -*-
from ag.gestion import consts
from ag.gestion.models import Participant, Invite, Activite, StatutParticipant
from django.dispatch.dispatcher import Signal

from ag.inscription.models import Forfait

inscription_transferee = Signal()


def statut_par_defaut(inscription):
    statut_etablissement = inscription.get_etablissement().statut
    if inscription.est_pour_mandate():
        if statut_etablissement == 'T':
            code_statut = 'repr_tit'
        else:
            assert statut_etablissement == 'A'
            code_statut = 'repr_assoc'
    else:
        code_statut = 'accomp'
    return StatutParticipant.objects.get(code=code_statut)


def transfere(inscription, statut, prise_en_charge_transport,
              prise_en_charge_hebergement, facturer_supplement_chambre_double):
    if Participant.objects.filter(inscription=inscription).count():
        raise Exception(u"Cette inscription a déjà été transférée")
    participant = Participant()
    participant.inscription = inscription
    participant.genre = inscription.genre
    participant.nom = inscription.nom
    participant.prenom = inscription.prenom
    participant.adresse = inscription.adresse
    participant.ville = inscription.ville
    participant.code_postal = inscription.code_postal
    participant.pays = inscription.pays
    participant.poste = inscription.poste
    participant.telephone = inscription.telephone
    participant.telecopieur = inscription.telecopieur
    participant.nationalite = inscription.nationalite
    participant.date_naissance = inscription.date_naissance
    participant.courriel = inscription.courriel
    participant.date_arrivee_hotel = inscription.date_arrivee_hotel
    participant.date_depart_hotel = inscription.date_depart_hotel
    participant.statut = statut
    participant.save()
    participant.forfaits.add(Forfait.objects.get(
        code=consts.CODE_FRAIS_INSCRIPTION))
    if inscription.accompagnateur:
        invite = Invite()
        invite.genre = inscription.accompagnateur_genre
        invite.nom = inscription.accompagnateur_nom
        invite.prenom = inscription.accompagnateur_prenom
        invite.participant = participant
        invite.save()
    if inscription.programmation_soiree_9_mai:
        activite = Activite.objects.get(code=consts.CODE_SOIREE_9_MAI)
        participant.inscrire_a_activite(
            activite, inscription.programmation_soiree_9_mai_invite)
    if inscription.programmation_soiree_10_mai:
        activite = Activite.objects.get(code=consts.CODE_SOIREE_10_MAI)
        participant.inscrire_a_activite(
            activite, inscription.programmation_soiree_10_mai_invite)
    if inscription.programmation_gala:
        activite = Activite.objects.get(code=consts.CODE_GALA)
        participant.inscrire_a_activite(
            activite, inscription.programmation_gala_invite)
    if inscription.programmation_soiree_12_mai:
        activite = Activite.objects.get(code=consts.CODE_COCKTAIL_12_MAI)
        participant.inscrire_a_activite(activite, False)
    participant.set_infos_depart_arrivee(inscription)
    participant.prise_en_charge_transport = prise_en_charge_transport
    if prise_en_charge_transport:
        participant.transport_organise_par_auf = True
    if prise_en_charge_hebergement:
        participant.reservation_hotel_par_auf = True
    participant.prise_en_charge_sejour = prise_en_charge_hebergement
    if facturer_supplement_chambre_double:
        participant.forfaits.add(Forfait.objects.get(
            code=consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE))
    participant.type_institution = 'E'
    participant.etablissement = inscription.get_etablissement()
    participant.save()
    inscription_transferee.send_robust(participant)
    return participant
