# -*- encoding: utf-8 -*-
"""
Fonctions de vérification des participants:
-------------------------------------------

Les types de problèmes possibles viennent du modèle "Probleme".


"""
from models import Probleme

def verifier_participant(participant):
    """
    Dresse la liste des problèmes du dossier du participant passé en paramètre
    """
    liste_erreurs = []
    if not participant.desactive:
        liste_erreurs.extend(_verifier_hotels(participant))

    for probleme in participant.problemes.all():
        if not  probleme.code in liste_erreurs:
            participant.problemes.remove(probleme)

    codes_problemes = [probleme.code for probleme in participant.problemes.all()]
    for code_erreur in liste_erreurs:
        if not code_erreur in codes_problemes:
            participant.problemes.add(Probleme.objects.get(code=code_erreur))

def _verifier_hotels(participant):
    erreurs = []
    if not participant.hotel:
        if participant.prise_en_charge_sejour:
            erreurs.append('hotel_manquant_1')
        if participant.chambres_reservees():
            erreurs.append('hotel_manquant_2')
    else:
        places_chambres = dict([(chambre.type_chambre, chambre.places)
            for chambre in participant.hotel.chambre_set.all()])
        nb_places = sum([reservation.nombre * places_chambres[reservation.type_chambre]
            for reservation in participant.reservationchambre_set.all()
            ])
        if participant.nombre_invites() + 1 != nb_places:
            erreurs.append('nb_places_hotel')
    return erreurs

def _verifier_prise_en_charge(participant):
    pass
#
#    erreurs = []
#    pec_inscription_ok = \
#        participant.statut.code in ('memb_inst', 'pers_auf', '')
