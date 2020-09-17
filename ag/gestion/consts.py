# -*- encoding: utf-8 -*-

# noinspection PyUnresolvedReferences
from ag.reference.models import (
    CODE_TITULAIRE,
    CODE_ASSOCIE,
    CODE_CENTRE_RECHERCHE,
    CODE_ETAB_ENSEIGNEMENT,
    CODE_RESEAU,
)


ARRIVEE_SEULEMENT = 0
DEPART_SEULEMENT = 1
VOL_ORGANISE = 2
VOL_GROUPE = 3

CODE_PAYS_FRANCE = 'FR'
CODE_PAYS_CANADA = 'CA'

CODE_AFRIQUE_CENTRALE = 'ACGL'
CODE_AFRIQUE_OUEST = 'AO'
CODE_AMERIQUE_NORD = 'A'
CODE_AMERIQUE_SUD = 'C'
CODE_ASIE_PACIFIQUE = 'AP'
CODE_EUROPE_EST = 'ECO'
CODE_EUROPE_OUEST = 'EO'
CODE_MAGHREB = 'M'
CODE_MOYEN_ORIENT = 'MO'
CODE_OCEAN_INDIEN = 'OI'

REG_AFRIQUE = 'AF'
REG_AMERIQUES = 'AM'
REG_ASIE_PACIFIQUE = 'AP'
REG_EUROPE_EST = 'EE'
REG_EUROPE_OUEST = 'EO'
# REG_FRANCE = 'FR'
REG_MOYEN_ORIENT = 'MO'
REG_MAGHREB = 'MG'
# REG_RESEAU = 'RI'

REGIONS_VOTANTS_CONSTS_DICT = {
    'REG_AFRIQUE': REG_AFRIQUE,
    'REG_AMERIQUES': REG_AMERIQUES,
    'REG_ASIE_PACIFIQUE': REG_ASIE_PACIFIQUE,
    'REG_EUROPE_EST': REG_EUROPE_EST,
    'REG_EUROPE_OUEST': REG_EUROPE_OUEST,
    # 'REG_FRANCE': REG_FRANCE,
    'REG_MOYEN_ORIENT': REG_MOYEN_ORIENT,
    'REG_MAGHREB': REG_MAGHREB,
    # 'REG_RESEAU': REG_RESEAU
}

REGIONS_VOTANTS = (
    (REG_AFRIQUE, 'Afrique'),
    (REG_AMERIQUES, 'Amériques'),
    (REG_ASIE_PACIFIQUE, "Asie-Pacifique"),
    (REG_EUROPE_EST, "Europe Centrale et Orientale"),
    (REG_EUROPE_OUEST, "Europe de l'Ouest"),
    # (REG_FRANCE, u"France"),
    (REG_MOYEN_ORIENT, "Moyen-Orient"),
    (REG_MAGHREB, "Maghreb"),
    # (REG_RESEAU, u"Réseau institutionnel"),
)

REGIONS_VOTANTS_DICT = dict(REGIONS_VOTANTS)

REGION_AUF_REGION_VOTANTS = {
    CODE_AFRIQUE_CENTRALE: REG_AFRIQUE,
    CODE_AFRIQUE_OUEST: REG_AFRIQUE,
    CODE_AMERIQUE_NORD: REG_AMERIQUES,
    CODE_AMERIQUE_SUD: REG_AMERIQUES,
    CODE_ASIE_PACIFIQUE: REG_ASIE_PACIFIQUE,
    CODE_EUROPE_EST: REG_EUROPE_EST,
    CODE_EUROPE_OUEST: REG_EUROPE_OUEST,
    CODE_MAGHREB: REG_MAGHREB,
    CODE_MOYEN_ORIENT: REG_MOYEN_ORIENT,
    CODE_OCEAN_INDIEN: REG_AFRIQUE,
}

ELEC_PRES = 'pres'
ELEC_CA = 'ca'
ELEC_CASS_ASS = 'cass-ass'
ELEC_CASS_TIT = 'cass-tit'
ELEC_CASS_RES = 'cass-res'


DANS_LA_COURSE = 'dans_course'
ELU = 'elu'
ELIMINE = 'elimine'

STATUTS_CANDIDATS = (
    (DANS_LA_COURSE, 'Dans la course'),
    (ELU, 'Élu'),
    (ELIMINE, 'Éliminé'),
)


CHAMBRE_SIMPLE = 'S'
CHAMBRE_DOUBLE = 'D'
CHAMBRE_SIMPLE_SUP = '1'
CHAMBRE_DOUBLE_SUP = '2'
CHAMBRE_LUXO = 'L'
CHAMBRE_ANTI_ALLERGENIQUE = 'A'

TYPES_CHAMBRES = (
    {
        'code': CHAMBRE_SIMPLE,
        'libelle_sing': 'Chambre simple',
        'libelle_plur': 'Chambres simples',
    },
    {
        'code': CHAMBRE_DOUBLE,
        'libelle_sing': 'Chambre double',
        'libelle_plur': 'Chambres doubles',
    },
    {
        'code': CHAMBRE_SIMPLE_SUP,
        'libelle_sing': 'Chambre simple supérieure',
        'libelle_plur': 'Chambres simples supérieures',
    },
    {
        'code': CHAMBRE_DOUBLE_SUP,
        'libelle_sing': 'Chambre double supérieure',
        'libelle_plur': 'Chambres doubles supérieures',
    },
    {
        'code': CHAMBRE_LUXO,
        'libelle_sing': 'Chambre Luxo (simple)',
        'libelle_plur': 'Chambres Luxo (simples)',
    },
    {
        'code': CHAMBRE_ANTI_ALLERGENIQUE,
        'libelle_sing': 'Chambre anti-allergénique',
        'libelle_plur': 'Chambres anti-allergéniques',
    },
)

TYPE_CHAMBRE_CHOICES = [(type['code'], type['libelle_sing'])
                        for type in TYPES_CHAMBRES]
BUREAU_REGION = '0'
COMPTOIR_COMPAGNIE = '1'
COURRIER_POSTAL = '2'
BUREAU_REGION_TRAIN = '3'
COMPTOIR_COMPAGNIE_TRAIN = '4'

PROBLEME_ERREUR = 'error'
PROBLEME_AVERTISSEMENT = 'warning'

PROBLEMES = {
    'hotel_manquant': {
        'sql_expr': 'hotel_manquant',
        'libelle': "Le séjour est pris en charge, mais aucun hôtel n'a été "
                   "sélectionné.",
        'libelle_court': "Hôtel non sélectionné",
        'niveau': PROBLEME_AVERTISSEMENT,
    },
    'reservation_hotel_manquante': {
        'sql_expr': 'reservation_hotel_manquante',
        'libelle': "Le séjour est pris en charge, mais aucun hébergement "
                   "n'a été réservé par l'AUF.",
        'libelle_court': "Réservation d'hôtel manquante",
        'niveau': PROBLEME_AVERTISSEMENT,
    },
    'trajet_manquant': {
        'sql_expr': 'trajet_manquant',
        'libelle': "Le transport est organisé par l'AUF mais le trajet "
                   "n'est pas déterminé.",
        'libelle_court': "Trajet manquant",
        'niveau': PROBLEME_AVERTISSEMENT,
    },
    'transport_non_organise': {
        'sql_expr': 'transport_non_organise',
        'libelle': "Le transport du participant est pris en charge mais "
                   "n'est pas organisé.",
        'libelle_court': "Transport non organisé",
        'niveau': PROBLEME_AVERTISSEMENT,
    },
    'prise_en_charge_a_completer': {
        'sql_expr': 'prise_en_charge_a_completer',
        'libelle': "Prise en charge à compléter.",
        'libelle_court': "Prise en charge à compléter",
        'niveau': PROBLEME_ERREUR,
    },
    'nb_places_incorrect': {
        'sql_expr': 'nb_places_incorrect',
        'libelle': "Le nombre de places réservées à l'hôtel ne correspond pas"
                   " au nombre de participants et d'invités.",
        'libelle_court': "Nombre de places incorrect",
        'niveau': PROBLEME_ERREUR,
    },
    'delinquant': {
        'sql_expr': 'delinquant',
        'libelle': "L'établissement a 3 années ou plus de cotisations "
                   "impayées.",
        'libelle_court': "Cotisations impayées",
        'niveau': PROBLEME_ERREUR,
    },
    'solde_a_payer': {
        'sql_expr': 'solde_a_payer',
        'libelle': "Il reste un solde à payer.",
        'libelle_court': "Solde à payer",
        'niveau': PROBLEME_ERREUR,
    },
    'paiement_en_trop': {
        'sql_expr': 'paiement_en_trop',
        'libelle': "Paiement en trop.",
        'libelle_court': "Paiement en trop",
        'niveau': PROBLEME_AVERTISSEMENT,
    },
}

EXCEPTIONS_DOM_TOM = (
    # Université des Antilles et de la Guyane, Pointe-à-Pitre
    # (Guadeloupe) France
    302,
    # Ecole supérieure d'art de La Réunion, Le Port - La Réunion, France
    806,
    # Université de La Réunion, Saint-Denis Messag (La Réunion), France
    242,
    # Université de la Nouvelle-Calédonie, Nouméa (Nouvelle-Calédonie),
    # France
    240,
    # Université de la Polynésie française, Faa'a – Tahiti (Polynésie
    # française), France
    241,
    1410,
)

PERM_MODIF_RENSEIGNEMENTS_PERSONNELS = 'renseignements_personnels'
PERM_MODIF_FACTURATION = 'facturation'
PERM_MODIF_SEJOUR = 'sejour'
PERM_MODIF_FICHIERS = 'fichiers'
PERM_MODIF_SUIVI = 'suivi'
PERM_LECTURE = 'lecture'
PERM_MODIF_NOTES_DE_FRAIS = 'notes_de_frais'
PERM_SUPPRESSION = 'suppression'
PERM_TRANSFERT_INSCRIPTION = 'transfert_inscription'


PERMS_DICT = {
    'PERM_MODIF_RENSEIGNEMENTS_PERSONNELS':
    PERM_MODIF_RENSEIGNEMENTS_PERSONNELS,
    'PERM_MODIF_FACTURATION': PERM_MODIF_FACTURATION,
    'PERM_MODIF_NOTES_DE_FRAIS': PERM_MODIF_NOTES_DE_FRAIS,
    'PERM_MODIF_SEJOUR': PERM_MODIF_SEJOUR,
    'PERM_MODIF_FICHIERS': PERM_MODIF_FICHIERS,
    'PERM_MODIF_SUIVI': PERM_MODIF_SUIVI,
    'PERM_LECTURE': PERM_LECTURE,
    'PERM_SUPPRESSION': PERM_SUPPRESSION,
    'PERM_TRANSFERT_INSCRIPTION': PERM_TRANSFERT_INSCRIPTION,
    }

ROLE_COMPTABLE = 'C'
ROLE_SAI = 'I'
ROLE_LECTEUR = 'L'
ROLE_ADMIN = 'A'
ROLE_SEJOUR = 'S'

# Permis si la permission est sans région ou si la région de la permission
# est la même que celle du participant
ALLOWED = (
    (PERM_MODIF_FACTURATION, ROLE_COMPTABLE),
    (PERM_MODIF_RENSEIGNEMENTS_PERSONNELS, ROLE_SAI),
    (PERM_MODIF_SUIVI, ROLE_SAI),
    (PERM_MODIF_SUIVI, ROLE_COMPTABLE),
    (PERM_MODIF_SUIVI, ROLE_SEJOUR),
    (PERM_MODIF_SEJOUR, ROLE_SEJOUR),
    (PERM_MODIF_NOTES_DE_FRAIS, ROLE_SAI),
    (PERM_MODIF_NOTES_DE_FRAIS, ROLE_SEJOUR),
    (PERM_MODIF_NOTES_DE_FRAIS, ROLE_COMPTABLE),
    (PERM_MODIF_FICHIERS, ROLE_SAI),
    (PERM_MODIF_FICHIERS, ROLE_SEJOUR),
    (PERM_MODIF_FICHIERS, ROLE_COMPTABLE),
    (PERM_TRANSFERT_INSCRIPTION, ROLE_SAI),
)

# Interdit si permission ne contient pas de région,
# permis si la région de la perm est la même que celle
# du participant
ALLOWED_MEME_REGION = (
    (PERM_MODIF_NOTES_DE_FRAIS, ROLE_LECTEUR),
    (PERM_MODIF_FICHIERS, ROLE_LECTEUR),
)

ARRIVEES = 'A'
DEPARTS = 'D'

PAIEMENT_CHOICES = (
    ('CB', 'Carte bancaire'),
    ('VB', 'Virement bancaire'),
    ('CE', 'Chèque en euros'),
    ('DL', 'Devises locales'),
)

PAIEMENT_CHOICES_DICT = dict(PAIEMENT_CHOICES)

CODE_CAT_INSCRIPTION = 'insc'
CODE_CAT_INVITE = 'invi'
CODE_CAT_HEBERGEMENT = 'hebe'

CATEGORIES_FORFAITS = (
    (CODE_CAT_INSCRIPTION, "Inscription"),
    (CODE_CAT_INVITE, "Invité"),
    (CODE_CAT_HEBERGEMENT, "Hébergement")
)

CODE_SOIREE_9_MAI = 'soiree_9_mai'
CODE_SOIREE_10_MAI = 'soiree_10_mai'
CODE_GALA = 'gala'
CODE_COCKTAIL_12_MAI = 'cocktail_12_mai'

CODES_ACTIVITES = (
    CODE_SOIREE_9_MAI, CODE_SOIREE_10_MAI,
    CODE_GALA, CODE_COCKTAIL_12_MAI
)

CODE_FRAIS_INSCRIPTION = 'inscription'
CODE_SOIREE_9_MAI_INVITE = '9_mai_invite'
CODE_SOIREE_10_MAI_INVITE = '10_mai_invite'
CODE_GALA_INVITE = 'gala_invite'
CODE_SUPPLEMENT_CHAMBRE_DOUBLE = 'chambre_double'
CODE_TRANSFERT_AEROPORT = 'trans_aeroport'
CODE_DEJEUNERS = 'dejeuners_invite'


CODES_FORFAITS = (
    CODE_FRAIS_INSCRIPTION,
    CODE_SOIREE_9_MAI_INVITE,
    CODE_SOIREE_10_MAI_INVITE,
    CODE_GALA_INVITE,
    CODE_SUPPLEMENT_CHAMBRE_DOUBLE,
    CODE_TRANSFERT_AEROPORT,
    CODE_DEJEUNERS,
)

TYPE_INST_AUCUNE = 'aucune'
TYPE_INST_ETABLISSEMENT = 'etablissement'

FONCTION_REPR_UNIVERSITAIRE = 'repr_uni'
FONCTION_ACCOMP_UNIVERSITAIRE = 'accomp_uni'
FONCTION_INSTANCE_SEULEMENT = 'instance_seul'
FONCTION_PERSONNEL_AUF = 'personnel_auf'

CAT_FONCTION_OBSERVATEUR = 'observ'


CA = 'A'
CS = 'S'
COS = 'O'

POINT_DE_SUIVI_NOTE_VERSEE = 'note_versee'

MARRAKECH = 'Marrakech'
CASABLANCA = 'Casablanca'
VILLE_AG = MARRAKECH

AEROPORTS_AG = (MARRAKECH, CASABLANCA)

AEROPORTS_CHOICES = tuple((a, a) for a in AEROPORTS_AG)
