# -*- encoding: utf-8 -*-

from django.core.cache import cache

MONTANTS_DATA = {
    'frais_inscription':
        {
            'montant': 330,
            'categorie': 'insc',
        },
    'supplement_chambre_double':
        {
            'montant': 100,
            'categorie': 'hebe',
        },
    'soiree_9_mai_membre':
        {
            # 'montant': 0, vient de la table activités
            'categorie': 'acti',
        },
    'soiree_9_mai_invite':
        {
            # 'montant': 0, vient de la table activités
            'categorie': 'acti',
        },
    'soiree_10_mai_membre':
        {
            # 'montant': 0,vient de la table activités
            'categorie': 'acti',
        },
    'soiree_10_mai_invite':
        {
            # 'montant': 0,vient de la table activités
            'categorie': 'acti',
        },
    'gala_membre':
        {
            # 'montant': 0,vient de la table activités
            'categorie': 'acti',
        },
    'gala_invite':
        {
            # 'montant': 0,vient de la table activités
            'categorie': 'acti',
        },
    'forfait_invite_dejeuners':
        {
             'montant': 30,
             'categorie': 'invite'
        },
    'forfait_invite_transfert':
        {
             'montant': 30,
             'categorie': 'invite'
        },
}


class InfosMontant(object):
    def __init__(self, data):
        self.__dict__.update(data)

    def affiche(self):
        if self.montant:
            return str(int(self.montant)) + u' €'
        else:
            return u'Inclus'


def get_montants_activite_from_db():
    from ag.gestion.models import Activite
    activites = Activite.objects.all()
    return {activite.code: (activite.prix, activite.prix_invite)
            for activite in activites}


CODES_MONTANTS_ACTIVITES = (
    ('soiree_9_mai', ('soiree_9_mai_membre', 'soiree_9_mai_invite')),
    ('soiree_10_mai', ('soiree_10_mai_membre', 'soiree_10_mai_invite')),
    ('gala', ('gala_membre', 'gala_invite')),
)


def init_montants():
    infos_montants = {}
    for code, infos_montants_data in MONTANTS_DATA.iteritems():
        infos_montants[code] = InfosMontant(infos_montants_data)
    montants_activites = get_montants_activite_from_db()
    for codes in CODES_MONTANTS_ACTIVITES:
        code_activite, (code_montant_membre, code_montant_invite) = codes
        montant_membre, montant_invite = montants_activites[code_activite]
        infos_montants[code_montant_membre].montant = montant_membre
        infos_montants[code_montant_invite].montant = montant_invite
    return infos_montants


def infos_montant_par_nom_champ(nom_champ):
    for infos_montant in get_infos_montants().itervalues():
        if hasattr(infos_montant, "nom_champ") and infos_montant.nom_champ == nom_champ:
            return infos_montant
    return None


def infos_montant_par_code(code):
    return get_infos_montants()[code]


def get_infos_montants():
    montants = cache.get('montants_inscription_ag', None)
    if not montants:
        montants = init_montants()
        cache.set('montants_inscription_ag', montants)

    return montants
