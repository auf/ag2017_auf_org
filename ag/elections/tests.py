# -*- coding: utf-8 -*-
from django.test import TestCase as DjangoTestCase

from ag.core.test_utils import ParticipantFactory, EtablissementFactory, \
    InvitationFactory
from ag.elections.models import *
from ag.gestion import consts
from ag.gestion.models import Fonction
from ag.inscription.models import Inscription
from ag.reference.models import Pays, Region
from ag.tests import create_fixtures


TITULAIRE = consts.CODE_TITULAIRE
ASSOCIE = consts.CODE_ASSOCIE
ESR = consts.CODE_ETAB_ENSEIGNEMENT
RES = consts.CODE_RESEAU


def create_etablissement(nom, pays, region, statut=TITULAIRE, qualite=ESR):
    return EtablissementFactory(
        nom=nom, pays=pays, region=region, statut=statut,
        qualite=qualite, membre=True)


class ElectionsCandidaturesTestCase(DjangoTestCase):
    fixtures = ['elections.json']

    def setUp(self):
        super(ElectionsCandidaturesTestCase, self).setUp()
        create_fixtures(self)
        region_mo = Region.objects.create(code=u'MO',
                                          nom=u'Moyen-Orient')
        region_eo = Region.objects.create(code=u'EO',
                                          nom=u"Europe de l'Ouest")
        pays_fr = Pays.objects.create(
            nom=u"France", code=u"FR", sud=False)
        pays_de = Pays.objects.create(
            nom=u"Allemagne", code=u"DE", sud=False)
        pays_eg = self.pays_eg = Pays.objects.create(
            nom=u"Égypte", code=u"EG", sud=True)
        pays_lb = self.pays_lb = Pays.objects.create(
            nom=u"Liban", code=u"LB", sud=True)
        etablissement_mo = create_etablissement(
            nom=u'etab_mo', pays=pays_eg, region=region_mo)
        etablissement_mo2 = create_etablissement(
            nom=u'etab_mo2', pays=pays_eg, region=region_mo)
        etablissement_mo3 = create_etablissement(
            nom=u'etab_mo3', pays=pays_lb, region=region_mo)
        etablissement_fr = create_etablissement(
            nom=u'etab_fr', pays=pays_fr, region=region_eo)
        etablissement_de = create_etablissement(
            nom=u'etab_de', pays=pays_de, region=region_eo)
        etablissement_reseau = create_etablissement(
            nom=u'etab_reseau', pays=pays_eg, region=region_mo,
            qualite=RES)
        etablissement_associe = create_etablissement(
            u'etab assoc', pays_eg, region_mo, statut=ASSOCIE)

        fonctions = dict((fonction.code, fonction)
                         for fonction in Fonction.objects.all())

        def creer_participant_vote(
                etablissement, pour_mandate=True,
                code_fonction=consts.FONCTION_REPR_UNIVERSITAIRE,
                nom=None, election=None):
            invitation = InvitationFactory(
                pour_mandate=pour_mandate,
                etablissement=etablissement)
            inscription = Inscription.objects.create(invitation=invitation)
            participant = ParticipantFactory(
                etablissement=etablissement,
                inscription=inscription,
                fonction=fonctions[code_fonction],
                candidat_a=election,
                **({'nom': nom} if nom else {})
            )
            return participant

        elec_ca = self.election_ca = Election.objects.get(code=consts.ELEC_CA)
        elections = Election.objects.all()
        self.participant_mo = creer_participant_vote(
            etablissement_mo, nom='A', election=elec_ca)
        self.participant_mo2 = creer_participant_vote(etablissement_mo2,
                                                      nom='B')
        self.participant_mo3 = creer_participant_vote(etablissement_mo3,
                                                      nom='C')
        self.participant_fr = creer_participant_vote(etablissement_fr)
        self.participant_fr_sans_vote = creer_participant_vote(
            etablissement_fr, pour_mandate=False,
            code_fonction=consts.FONCTION_ACCOMP_UNIVERSITAIRE)
        self.participant_de = creer_participant_vote(etablissement_de)
        self.participant_reseau_mo = creer_participant_vote(
            etablissement_reseau, nom='D', election=elec_ca)
        self.participant_associe = creer_participant_vote(etablissement_associe)
        self.criteria = get_electeur_criteria()
        self.candidats_criteria = get_all_listes_candidat_criteria(elections)
        self.candidats = get_candidats_possibles()

    def get_participants_region(self, code_region):
        code = code_critere_region(code_region)
        crit = self.criteria[code]
        return list(filter_participants(crit.filter))

    def test_crit_region_mo(self):
        participants = self.get_participants_region(consts.REG_MOYEN_ORIENT)
        self.assertEqual(set(participants),
                         {self.participant_mo,
                          self.participant_mo2,
                          self.participant_mo3,
                          self.participant_reseau_mo})

    def test_crit_reseau(self):
        crit = self.criteria[CRITERE_RESEAU]
        self.assertEqual(
            set(filter_participants(crit.filter)),
            {self.participant_reseau_mo}
        )

    def test_crit_assoc(self):
        crit = self.criteria[CRITERE_ASSOCIES]
        self.assertEqual(
            set(filter_participants(crit.filter)),
            {self.participant_associe}
        )

    def test_donnees_liste_salle_mo(self):
        code_critere = code_critere_region(consts.REG_MOYEN_ORIENT)
        d = get_donnees_liste_salle(self.criteria[code_critere])
        self.assertDictEqual(
            d,
            {self.pays_eg.nom: [self.participant_mo, self.participant_mo2,
                                self.participant_reseau_mo],
             self.pays_lb.nom: [self.participant_mo3]}
        )

    def test_candidats_ca_mo(self):
        code_critere = code_critere_candidat_region(consts.ELEC_CA,
                                                    consts.REG_MOYEN_ORIENT)
        filter_ = self.candidats_criteria[code_critere].filter
        self.assertEqual(
            set(filter_participants(filter_)),
            {self.participant_mo, self.participant_reseau_mo}
        )

    def test_bulletin_ca_mo(self):
        d, _ = get_donnees_bulletin_ca()
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0]['code_region'], consts.REG_MOYEN_ORIENT)
        self.assertEqual(d[0]['nb_sieges'],
                         self.election_ca.nb_sieges_moyen_orient)
        self.assertEqual(len(d[0]['candidats']), 2)
