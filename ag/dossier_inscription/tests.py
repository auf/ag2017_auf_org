# -*- encoding: utf-8 -*-
import django.test
from ag.core.test_utils import InscriptionFactory, ParticipantFactory
from ag.dossier_inscription.models import (
    Adresse,
    InscriptionFermee, SuiviDossier)
from ag.gestion.models import COMPLETE


class InscriptionFermeeTests(django.test.TestCase):
    def test_get_adresse_self(self):
        """Si l'inscription n'a pas été validée, l'adresse retournée est
        l'adresse de l'objet Inscription.
        """
        adresse = Adresse(adresse="adr", code_postal="12345", ville="laville",
                          pays="unpays")
        i = InscriptionFermee(**adresse.__dict__)
        assert i.get_adresse() == adresse

    def test_get_adresse_participant(self):
        """Si l'inscription a été validée, un objet participant a été créé
        pour elle, et c'est l'adresse contenue dans Participant que get_adresse
        doit retourner.
        """
        adresse_part = Adresse(adresse="adrpart", code_postal="98765",
                               ville="lavillepart", pays="unpays")
        i = InscriptionFactory()
        ParticipantFactory(inscription=i, **adresse_part.__dict__)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_adresse() == adresse_part


class SuiviInscriptionTest(django.test.TestCase):
    def test_inscription_fermee(self):
        i = InscriptionFactory(fermee=True)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_suivi_dossier() == SuiviDossier(
            inscription_recue=True,
            inscription_validee=False,
            participation_confirmee=False,
            plan_de_vol_complete=False,
        )

    def test_inscription_fermee_et_validee(self):
        i = InscriptionFactory(fermee=True)
        ParticipantFactory(inscription=i)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_suivi_dossier() == SuiviDossier(
            inscription_recue=True,
            inscription_validee=True,
            participation_confirmee=False,
            plan_de_vol_complete=False,
        )

    def test_participation_facturation_validee(self):
        i = InscriptionFactory(fermee=True)
        ParticipantFactory(inscription=i, facturation_validee=True)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_suivi_dossier() == SuiviDossier(
            inscription_recue=True,
            inscription_validee=True,
            participation_confirmee=True,
            plan_de_vol_complete=False,
        )

    def test_participation_plan_de_vol_complet(self):
        i = InscriptionFactory(fermee=True)
        ParticipantFactory(inscription=i, facturation_validee=True,
                           statut_dossier_transport=COMPLETE)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_suivi_dossier() == SuiviDossier(
            inscription_recue=True,
            inscription_validee=True,
            participation_confirmee=True,
            plan_de_vol_complete=True,
        )
