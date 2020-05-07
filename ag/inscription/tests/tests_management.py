# -*- encoding: utf-8 -*-
from auf_django_mailing.models import ModeleCourriel
from django.core.management import call_command
import django.test
import pytest
from ag.core.test_utils import EtablissementFactory
from ag.inscription.management.commands.generer_invitations_mandates import \
    creer_invitation_enveloppe_mandate, get_etablissements_sans_invitation
from ag.inscription.models import InvitationEnveloppe
from ag.tests import make_modele_courriel_mandate, create_fixtures


class EnveloppeCreeTestCase(django.test.TestCase):
    def test_invitation_enveloppe_creee(self):
        modele = make_modele_courriel_mandate()
        etablissement = EtablissementFactory()
        creer_invitation_enveloppe_mandate(modele, etablissement)
        assert InvitationEnveloppe.objects.filter(
            invitation__etablissement=etablissement,
            invitation__pour_mandate=True,
            enveloppe__modele=modele).count() == 1


class EtablissementsSansInvitationTestCase(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super(EtablissementsSansInvitationTestCase, cls).setUpTestData()
        modele = make_modele_courriel_mandate()
        cls.etablissement_avec_invitation = EtablissementFactory(
            membre=True, responsable_courriel='a@b.com')
        creer_invitation_enveloppe_mandate(modele,
                                           cls.etablissement_avec_invitation)
        cls.etablissement_pas_encore_d_invitation = EtablissementFactory(
            membre=True, responsable_courriel='c@d.com')
        cls.etablissement_non_membre = EtablissementFactory(
            membre=False, responsable_courriel='e@f.com')
        modele2 = ModeleCourriel.objects.create(code='blabla', sujet='b',
                                                corps='c', html=False)
        cls.etablissement_avec_invitation_autre_modele = EtablissementFactory(
            membre=True, responsable_courriel='g@h.com')
        creer_invitation_enveloppe_mandate(
            modele2, cls.etablissement_avec_invitation_autre_modele)
        cls.etablissement_sans_courriel = EtablissementFactory(
            membre=True, responsable_courriel='')
        cls.etablissements_sans_invitation = get_etablissements_sans_invitation(
            modele)

    def test_deja_invite(self):
        assert self.etablissement_avec_invitation not in \
               self.etablissements_sans_invitation

    def test_pas_encore_invite(self):
        assert self.etablissement_pas_encore_d_invitation in \
               self.etablissements_sans_invitation

    def test_invite_autre_modele(self):
        assert self.etablissement_avec_invitation_autre_modele in \
               self.etablissements_sans_invitation

    def test_sans_courriel(self):
        assert self.etablissement_sans_courriel not in \
               self.etablissements_sans_invitation

    def test_non_membre(self):
        assert self.etablissement_non_membre not in \
               self.etablissements_sans_invitation
