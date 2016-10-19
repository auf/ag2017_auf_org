# -*- encoding: utf-8 -*-

from django.core.cache import cache

MONTANTS_DATA = {
    'frais_inscription':
        {
            'montant': 400,
            'categorie': 'insc',
        },
    'supplement_chambre_double':
        {
            'montant': 30,
            'categorie': 'hebe',
        },
    'soiree_9_mai_invite':
        {
            # 'montant': 0, vient de la table activités
            'categorie': 'invite',
        },
    'soiree_10_mai_invite':
        {
            # 'montant': 0,vient de la table activités
            'categorie': 'invite',
        },
    'gala_invite':
        {
            # 'montant': 0,vient de la table activités
            'categorie': 'invite',
        },
    'forfait_invite_dejeuners':
        {
             'montant': 60,
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


def get_montants_activite_invite_from_db():
    from ag.gestion.models import Activite
    activites = Activite.objects.all()
    return {activite.code: activite.prix_invite
            for activite in activites}


CODES_MONTANTS_ACTIVITES = (
    ('soiree_9_mai', 'soiree_9_mai_invite'),
    ('soiree_10_mai', 'soiree_10_mai_invite'),
    ('gala', 'gala_invite'),
)


def init_montants():
    infos_montants = {}
    for code, infos_montants_data in MONTANTS_DATA.iteritems():
        infos_montants[code] = InfosMontant(infos_montants_data)
    montants_activites_invites = get_montants_activite_invite_from_db()
    for codes in CODES_MONTANTS_ACTIVITES:
        code_activite, code_montant_invite = codes
        montant_invite = montants_activites_invites[code_activite]
        infos_montants[code_montant_invite].montant = int(montant_invite)
    return infos_montants


def infos_montant_par_code(code):
    return get_infos_montants()[code]


def get_infos_montants():
    montants = cache.get('montants_inscription_ag', None)
    if not montants:
        montants = init_montants()
        cache.set('montants_inscription_ag', montants)

    return montants
