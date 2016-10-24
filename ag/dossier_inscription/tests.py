# -*- encoding: utf-8 -*-
import collections
import datetime
import django.test
from ag.core.test_utils import InscriptionFactory, ParticipantFactory
from ag.dossier_inscription.models import (
    InscriptionFermee, SuiviDossier)
from ag.gestion.models import COMPLETE
from ag.dossier_inscription import views
from ag.inscription.models import Adresse


class InscriptionFermeeTests(django.test.TestCase):
    def test_get_adresse_self(self):
        """Si l'inscription n'a pas été validée, l'adresse retournée est
        l'adresse de l'objet Inscription.
        """
        adresse = Adresse(adresse="adr", code_postal="12345", ville="laville",
                          pays="unpays", telephone='123-222-2222',
                          telecopieur='123-222-2222')
        i = InscriptionFermee(**adresse.__dict__)
        assert i.get_adresse() == adresse

    def test_get_adresse_participant(self):
        """Si l'inscription a été validée, un objet participant a été créé
        pour elle, et c'est l'adresse contenue dans Participant que get_adresse
        doit retourner.
        """
        adresse_part = Adresse(adresse="adrpart", code_postal="98765",
                               ville="lavillepart", pays="unpays",
                               telephone='123-222-2222',
                               telecopieur='123-222-2222')
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

FakeRequest = collections.namedtuple('FakeRequest', ('POST', 'method'))


class PlanVolFormTest(django.test.TestCase):
    def handle_plan_vol_form(self, inscription):
        request = FakeRequest({
            'arrivee_date': '01/05/2017',
            'arrivee_heure': '11:11',
            'arrivee_vol': 'AF123',
            'depart_date': '05/05/2017',
            'depart_heure': '12:12',
            'depart_vol': 'AF456',
            'submit-plan-vol-form': '1',
        }, 'POST')
        return views.handle_plan_vol_form(request, inscription)

    def test_avec_participant(self):
        """Le plan de vol est enregistré dans l'inscription et le participant,
        si l'inscription a été transférée dans le système de gestion.

        """
        i = InscriptionFactory(fermee=True)
        ParticipantFactory(inscription=i)
        i = InscriptionFermee.objects.get(pk=i.id)
        self.handle_plan_vol_form(i)
        p = i.get_participant()
        infos_arrivee = p.get_infos_arrivee()
        infos_depart = p.get_infos_depart()
        date_arrivee = datetime.date(2017, 05, 01)
        assert infos_arrivee.date_arrivee == i.arrivee_date == date_arrivee
        assert infos_arrivee.heure_arrivee == i.arrivee_heure == \
            datetime.time(11, 11)
        assert infos_arrivee.numero_vol == i.arrivee_vol == 'AF123'
        assert infos_depart.date_depart == i.depart_date
        assert infos_depart.heure_depart == i.depart_heure

    def test_sans_participant(self):
        """Le plan de vol est enregistré dans l'inscription seulement,
        si l'inscription n'a pas été transférée dans le système de gestion.

        """
        i = InscriptionFactory(fermee=True)
        i = InscriptionFermee.objects.get(id=i.id)
        self.handle_plan_vol_form(i)
        date_arrivee = datetime.date(2017, 5, 1)
        assert i.arrivee_date == date_arrivee
        assert i.arrivee_heure == datetime.time(11, 11)
        assert i.arrivee_vol == 'AF123'
        assert i.depart_date == datetime.date(2017, 5, 5)
        assert i.depart_heure == datetime.time(12, 12)
