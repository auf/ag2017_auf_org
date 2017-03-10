# -*- encoding: utf-8 -*-

from django.db.models import IntegerField, collections

from ag.core.models import TableReferenceOrdonnee
from ag.gestion import consts
import ag.gestion.models as gestion_models


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


Candidat = collections.namedtuple('Candidature', (
    'participant_id', 'participant_nom_complet',
    'participant_nom', 'participant_prenom',
    'participant_poste', 'participant_etablissement_nom',
    'election', 'suppleant_de_id', 'libre', 'elimine',
    'candidatures_possibles', 'code_region',
))


def participant_to_candidat(participant):
    return Candidat(
        participant_id=participant.id,
        participant_nom=participant.get_nom_complet(),
        election=participant.candidat_a_id,
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


class Candidats(object):
    def __init__(self, candidats):
        self.candidats = candidats
        self.suppleants = {c.suppleant_de_id: c.id
                           for c in self.candidats if c.suppleant_de_id}

    def get_suppleant(self, candidat):
        return self.suppleants.get(candidat.id, None)

    def get_suppleant_de_choices(self, candidat):
        return [c for c in self.candidats if c.election == consts.ELEC_CA
                if c.id != candidat.id]

    def grouped_by_region(self):
        enum_candidats = enumerate(self.candidats)
        sorted_enum = sorted(enum_candidats, lambda x: (x[1].code_region, x[0]))
        return [e[1] for e in sorted_enum]
