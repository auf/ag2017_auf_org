# -*- coding: utf-8 -*-
from django.test import TestCase as DjangoTestCase

from ag.core.test_utils import ParticipantFactory, EtablissementFactory, \
    InvitationFactory
from ag.elections.models import code_critere_region, get_electeur_criteria, \
    filter_participants, CRITERE_RESEAU, CRITERE_ASSOCIES, \
    get_candidats_possibles, get_donnees_liste_salle
from ag.gestion import consts
from ag.gestion.models import get_fonction_repr_universitaire, Invitation, \
    Fonction
from ag.inscription.models import Inscription
from ag.reference.models import Pays, Region, Etablissement
from ag.tests import create_fixtures, creer_participant


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

    @classmethod
    def setUpClass(cls):
        super(ElectionsCandidaturesTestCase, cls).setUpClass()
        create_fixtures(cls)
        region_mo = Region.objects.create(code=u'MO',
                                          nom=u'Moyen-Orient')
        region_eo = Region.objects.create(code=u'EO',
                                          nom=u"Europe de l'Ouest")
        pays_fr = Pays.objects.create(
            nom=u"France", code=u"FR", sud=False)
        pays_de = Pays.objects.create(
            nom=u"Allemagne", code=u"DE", sud=False)
        pays_eg = cls.pays_eg = Pays.objects.create(
            nom=u"Égypte", code=u"EG", sud=True)
        pays_lb = cls.pays_lb = Pays.objects.create(
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
                code_fonction=consts.FONCTION_REPR_UNIVERSITAIRE):
            invitation = InvitationFactory(
                pour_mandate=pour_mandate,
                etablissement=etablissement)
            inscription = Inscription.objects.create(invitation=invitation)
            participant = ParticipantFactory(
                etablissement=etablissement,
                inscription=inscription,
                fonction=fonctions[code_fonction],
            )
            return participant

        cls.participant_mo = creer_participant_vote(etablissement_mo)
        cls.participant_mo2 = creer_participant_vote(etablissement_mo2)
        cls.participant_mo3 = creer_participant_vote(etablissement_mo3)
        cls.participant_fr = creer_participant_vote(etablissement_fr)
        cls.participant_fr_sans_vote = creer_participant_vote(
            etablissement_fr, pour_mandate=False,
            code_fonction=consts.FONCTION_ACCOMP_UNIVERSITAIRE)
        cls.participant_de = creer_participant_vote(etablissement_de)
        cls.participant_reseau_mo = creer_participant_vote(etablissement_reseau)
        cls.participant_associe = creer_participant_vote(etablissement_associe)
        cls.criteria = get_electeur_criteria()
        cls.candidats = get_candidats_possibles()

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
        print(d)
        self.assertDictEqual(
            d,
            {self.pays_eg.nom: [self.participant_mo, self.participant_mo2,
                                self.participant_reseau_mo],
             self.pays_lb.nom: [self.participant_mo3]}
        )
