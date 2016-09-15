# -*- encoding: utf-8 -*-
from ag.gestion.models import Participant, Invite, Activite, StatutParticipant
from django.dispatch.dispatcher import Signal

inscription_transferee = Signal()

VILLE_AEROPORT = u'São Paulo'


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
    participant.paiement = inscription.paiement
    participant.statut = statut
    participant.save()
    if inscription.accompagnateur:
        invite = Invite()
        invite.genre = inscription.accompagnateur_genre
        invite.nom = inscription.accompagnateur_nom
        invite.prenom = inscription.accompagnateur_prenom
        invite.participant = participant
        invite.save()
    if inscription.programmation_soiree_9_mai:
        activite = Activite.objects.get(code="soiree_9_mai")
        participant.inscrire_a_activite(
            activite, inscription.programmation_soiree_9_mai_invite)
    if inscription.programmation_soiree_10_mai:
        activite = Activite.objects.get(code="soiree_10_mai")
        participant.inscrire_a_activite(
            activite, inscription.programmation_soiree_10_mai_invite)
    if inscription.programmation_gala:
        activite = Activite.objects.get(code="gala")
        participant.inscrire_a_activite(
            activite, inscription.programmation_gala_invite)
    if inscription.arrivee_date:
        participant.set_infos_arrivee(inscription.arrivee_date,
            inscription.arrivee_heure, inscription.arrivee_vol,
            inscription.arrivee_compagnie, VILLE_AEROPORT)
    if inscription.depart_date:
        participant.set_infos_depart(inscription.depart_date,
            inscription.depart_heure, inscription.depart_vol,
            inscription.depart_compagnie, inscription.get_depart_de_display())

    participant.prise_en_charge_transport = prise_en_charge_transport
    if prise_en_charge_transport:
        participant.transport_organise_par_auf = True
    if prise_en_charge_hebergement:
        participant.reservation_hotel_par_auf = True
    participant.prise_en_charge_sejour = prise_en_charge_hebergement
    participant.facturation_supplement_chambre_double = facturer_supplement_chambre_double
    participant.type_institution = 'E'
    participant.etablissement = inscription.get_etablissement()
    participant.accompte = inscription.paiement_paypal_total()
    participant.save()
    inscription_transferee.send_robust(participant)
    return participant


