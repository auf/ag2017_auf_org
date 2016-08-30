# -*- encoding: utf-8 -*-

from django.core.cache import cache

MONTANTS_DATA = {
    'frais_inscription':
        {
            'label': u'Frais d\'inscription',
            'montant': 330,
            'categorie': 'insc',
        },
    'frais_inscription_invite':
        {
            'label': u"Frais d\'inscription (invité)",
            'montant': 0,
            'nom_champ': 'accompagnateur',
            'valeur_champ': True,
            'categorie': 'insc',
        },
    'supplement_chambre_double':
        {
            'label': u"Supplément chambre double",
            'montant': 200,
            'categorie': 'hebe',
        },
    'sortie_unesp_membre':
        {
            'label': u"Soirée organisée par l'UNESP (membre)",
            # 'montant': 0, vient de la table activités
            'nom_champ': 'programmation_soiree_unesp',
            'valeur_champ': True,
            'categorie': 'acti',
        },
    'sortie_unesp_invite':
        {
            'label': u"Soirée organisée par l'UNESP (accompagnateur)",
            # 'montant': 0, vient de la table activités
            'nom_champ': 'programmation_soiree_unesp_invite',
            'valeur_champ': True,
            'categorie': 'acti',
        },
    'sortie_8_mai_membre':
        {
            'label': u"Soirée interconsulaire (membre)",
            # 'montant': 0,vient de la table activités
            'nom_champ': 'programmation_soiree_interconsulaire',
            'valeur_champ': True,
            'categorie': 'acti',
        },
    'sortie_8_mai_invite':
        {
            'label': u"Soirée interconsulaire (invité)",
            # 'montant': 0,vient de la table activités
            'nom_champ': 'programmation_soiree_interconsulaire_invite',
            'valeur_champ': True,
            'categorie': 'acti',
        },
    'gala_membre':
        {
            'label': u"Soirée de gala de clôture (membre)",
            # 'montant': 0,vient de la table activités
            'nom_champ': 'programmation_gala',
            'valeur_champ': True,
            'categorie': 'acti',
        },
    'gala_invite':
        {
            'label': u"Soirée de gala de clôture (accompagnateur)",
            # 'montant': 0,vient de la table activités
            'nom_champ': 'programmation_gala_invite',
            'valeur_champ': True,
            'categorie': 'acti',
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


def get_montant_activite_from_db(code):
    from ag.gestion.models import Activite
    activite = Activite.objects.get(code=code)
    return activite.prix, activite.prix_invite


def init_montants():
    montants = {}
    for code, infos_montants_data in MONTANTS_DATA.iteritems():
        montants[code] = InfosMontant(infos_montants_data)
    montants['sortie_unesp_membre'].montant, montants['sortie_unesp_invite'].montant \
        = get_montant_activite_from_db('unesp')
    montants['sortie_8_mai_membre'].montant, montants['sortie_8_mai_invite'].montant\
        = get_montant_activite_from_db('8_mai')
    montants['gala_membre'].montant, montants['gala_invite'].montant\
        = get_montant_activite_from_db('gala')
    return montants


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
