# -*- encoding: utf-8 -*-

import collections

import itertools

import functools
from django.db.models import IntegerField

from ag.core.models import TableReferenceOrdonnee
from ag.gestion import consts
import ag.gestion.models as gestion_models
from ag.gestion.participants_queryset import ParticipantsQuerySet


class Election(TableReferenceOrdonnee):
    class Meta:
        ordering = ['ordre']

    nb_sieges_global = IntegerField(u"Global", blank=True, null=True)
    nb_sieges_afrique = IntegerField(u"Afrique", blank=True, null=True)
    nb_sieges_ameriques = IntegerField(u"Amériques", blank=True, null=True)
    nb_sieges_asie_pacifique = IntegerField(u"Asie-Pacifique",
                                            blank=True, null=True)
    nb_sieges_europe_ouest = IntegerField(u"Europe de l'ouest",
                                          blank=True, null=True)
    nb_sieges_europe_est = IntegerField(u"Europe centrale et orientale",
                                        blank=True, null=True)
    nb_sieges_maghreb = IntegerField(u"Maghreb", blank=True, null=True)
    nb_sieges_moyen_orient = IntegerField(u"Moyen-Orient", blank=True,
                                          null=True)

    def __unicode__(self):
        return self.code


Candidat = collections.namedtuple('Candidat', (
    'participant_id', 'nom_complet',
    'nom', 'prenom',
    'poste', 'etablissement_nom',
    'code_election', 'suppleant_de_id', 'libre', 'elimine',
    'candidatures_possibles', 'code_region',
))


def participant_to_candidat(participant):
    if participant.candidat_a:
        code_election = participant.candidat_a.code
    else:
        code_election = None
    return Candidat(
        participant_id=participant.id,
        nom_complet=participant.get_nom_complet(),
        nom=participant.nom,
        prenom=participant.prenom,
        poste=participant.poste,
        etablissement_nom=participant.etablissement.nom,
        code_election=code_election,
        suppleant_de_id=participant.suppleant_de_id,
        libre=participant.candidat_libre,
        elimine=participant.candidat_elimine,
        candidatures_possibles=participant.candidatures_possibles(),
        code_region=participant.get_region_vote_display(),
    )


def get_candidats_possibles():
    participants = gestion_models.Participant.actifs \
        .all().filter_representants_mandates() \
        .avec_region_vote() \
        .select_related('candidat_a', 'suppleant_de')\
        .order_by('nom', 'prenom')
    return Candidats([participant_to_candidat(p) for p in participants])


def peut_avoir_suppleant(candidat):
    return candidat.code_election == consts.ELEC_CA


def peut_etre_suppleant(candidat):
    return consts.ELEC_CA in candidat.candidatures_possibles


def suppleant_possible(candidat, suppleant):
    return peut_avoir_suppleant(candidat) and\
        peut_etre_suppleant(suppleant) and\
        candidat.code_region == suppleant.code_region


class Candidats(object):
    def __init__(self, candidats):
        self.candidats = candidats
        self.suppleants = {c.suppleant_de_id: c
                           for c in self.candidats if c.suppleant_de_id}
        self.candidats_dict = {c.participant_id: c for c in self.candidats}

    def __len__(self):
        return len(self.candidats)

    def get_candidat(self, participant_id):
        return self.candidats_dict[participant_id]

    def get_suppleant(self, candidat):
        return self.suppleants.get(candidat.participant_id, None)

    def get_suppleant_de_choices(self, candidat):
        suppleants_de_possibles = [
            (c.participant_id, c.nom_complet)
            for c in self.candidats
            if suppleant_possible(c, candidat) and
            (c.participant_id == candidat.suppleant_de_id or
             not self.get_suppleant(c))]
        return [(u"", u"Personne")] + suppleants_de_possibles

    def grouped_by_region(self):
        enum_candidats = enumerate(self.candidats)
        sorted_enum = sorted(enum_candidats,
                             key=lambda x: (x[1].code_region, x[0]))
        return [e[1] for e in sorted_enum]

    def update_participants(self):
        elections_by_code = {e.code: e for e in Election.objects.all()}
        participant_ids = [c.participant_id for c in self.candidats]
        participants = list(gestion_models.Participant.objects
                            .filter(id__in=participant_ids)
                            .avec_region_vote()
                            .select_related('candidat_a', 'suppleant_de'))
        participant_by_id = {p.id: p for p in participants}
        for candidat in self.candidats:
            if candidat.code_election:
                election = elections_by_code[candidat.code_election]
            else:
                election = None
            participant = participant_by_id[candidat.participant_id]
            participant.candidat_a = election
            participant.candidat_libre = candidat.libre
            participant.candidat_elimine = candidat.elimine

        for candidat in self.candidats:
            participant = participant_by_id[candidat.participant_id]
            if candidat.suppleant_de_id:
                suppleant_de = self.candidats_dict[candidat.suppleant_de_id]
                if suppleant_possible(suppleant_de, candidat):
                    participant.suppleant_de = \
                        participant_by_id[candidat.suppleant_de_id]
                else:
                    participant.suppleant_de = None
            else:
                participant.suppleant_de = None

        for participant in participants:
            participant.save()

CritereElecteur = collections.namedtuple(
    'CritereElecteur', ('code', 'titre', 'filter', ))


def make_filter_region(code_region):
    def filter_region(participants_queryset):
        return participants_queryset.filter_region_vote(code_region)

    return filter_region


def filter_participants(filters):
    qs = gestion_models.Participant.objects.actifs().represente_etablissement()
    for filtr in filters:
        qs = filtr(qs)
    return qs


CRITERE_REGION_TEMPLATE = 'membre_tit_{}'
CRITERE_ASSOCIES = 'associes'
CRITERE_RESEAU = 'reseau'

CRITERE_CANDIDAT_ASSOCIE = 'associe'
CRITERE_CANDIDAT_RESEAU = 'reseau'


def code_critere_region(code_region):
    return CRITERE_REGION_TEMPLATE.format(code_region)


def get_electeur_criteria():
    criteria = []
    for code_region, nom_region in consts.REGIONS_VOTANTS_DICT.iteritems():
        criteria.append(CritereElecteur(
            code=code_critere_region(code_region),
            filter=(ParticipantsQuerySet.titulaires,
                    make_filter_region(code_region)),
            titre=u"Membres titulaires - {}".format(nom_region), ))
    criteria.append(CritereElecteur(
        code=CRITERE_RESEAU,
        filter=(ParticipantsQuerySet.titulaires,
                ParticipantsQuerySet.reseau),
        titre=u"Membres titulaires des réseaux"
    ))
    criteria.append(CritereElecteur(
        code=CRITERE_ASSOCIES,
        filter=(ParticipantsQuerySet.associes, ),
        titre=u"Membres associés"
    ))
    return collections.OrderedDict(((c.code, c) for c in criteria))


def code_critere_candidat_region(code_election, code_region):
    return '{}_{}'.format(code_election, code_region)


def titre_liste_candidats(election):
    return u"Candidats - {}".format(election.libelle)


def make_filter_election(election):
    return functools.partial(ParticipantsQuerySet.candidats,
                             code_election=election.code)


CritereCandidat = collections.namedtuple(
    'CritereCandidat', ('code', 'titre', 'filter',
                        'code_region', 'code_election', ))


def get_listes_candidat_par_region_criteria(election):
    """

    :param election: Election
    :return: list[CritereCandidat]
    """
    criteria = []
    filter_election = make_filter_election(election)
    base_titre = titre_liste_candidats(election)
    for code_region, nom_region in consts.REGIONS_VOTANTS_DICT.iteritems():
        criteria.append(CritereCandidat(
            code=code_critere_candidat_region(election.code, code_region),
            titre=u"{} - Membres titulaires {}".format(base_titre, nom_region),
            filter=(filter_election,
                    make_filter_region(code_region)),
            code_region=code_region,
            code_election=election.code,
        ))
    return criteria


def get_all_listes_candidat_criteria(elections):
    criteria = []
    liste_par_region = {consts.ELEC_CA, consts.ELEC_PRES,
                        consts.ELEC_CASS_TIT}
    for election in elections:
        if election.code in liste_par_region:
            criteria.extend(get_listes_candidat_par_region_criteria(election))
        else:
            criteria.append(
                CritereCandidat(
                    code=election.code,
                    titre=titre_liste_candidats(election),
                    filter=(make_filter_election(election), ),
                    code_region=None,
                    code_election=election.code,
                )
            )
    return collections.OrderedDict(((c.code, c) for c in criteria))


def get_donnees_liste_salle(critere):
    participants = filter_participants(critere.filter)
    participants = participants\
        .order_by('etablissement__pays__nom', 'nom', 'prenom')\
        .select_related('etablissement')
    participants = list(participants)
    grouped_participants = itertools.groupby(
        participants, key=lambda p: p.etablissement.pays.nom)
    return dict((pays, list(liste)) for pays, liste in grouped_participants)


