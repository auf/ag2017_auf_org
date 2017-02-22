# -*- encoding: utf-8 -*-
import collections
import datetime
import django.test
from django.core.urlresolvers import reverse

from ag.core.test_utils import (
    InscriptionFactory,
    ParticipantFactory)
from ag.dossier_inscription.models import (
    InscriptionFermee,
    SuiviDossier)
from ag.gestion import transfert_inscription
from ag.gestion.models import COMPLETE, Participant
from ag.dossier_inscription import views
from ag.inscription.models import Adresse, PaypalResponse
from ag.tests import forfaits_fixture, fonction_fixture


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

    def create_inscription_paiement(self):
        forfaits_fixture()
        i = InscriptionFactory()
        PaypalResponse.objects.create(
            inscription=i, type_reponse='IPN', montant=100,
            validated=True, statut='Completed')
        return InscriptionFermee.objects.get(id=i.id)

    def test_get_solde_sans_participant(self):
        i = self.create_inscription_paiement()
        assert i.get_solde() == (i.total_facture - i.total_deja_paye)

    def test_get_solde_avec_participant(self):
        fonction_fixture()
        i = self.create_inscription_paiement()
        p = transfert_inscription.transfere(i, False, False, False)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_solde() == (i.total_facture - i.total_deja_paye)


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
        dossier = inscription.dossier
        request = FakeRequest({
            'arrivee_date': '01/05/2017',
            'arrivee_heure': '11:11',
            'arrivee_vol': 'AF123',
            'depart_date': '05/05/2017',
            'depart_heure': '12:12',
            'depart_vol': 'AF456',
            'depart_de': 'Marrakech',
            'arrivee_a': 'Casablanca',
            'submit-plan-vol-form': '1',
        }, 'POST')
        form = views.handle_plan_vol_form(request, dossier)
        assert not form.errors
        return form

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
        date_depart = datetime.date(2017, 05, 05)
        assert infos_arrivee.date_arrivee == date_arrivee
        assert infos_arrivee.heure_arrivee == datetime.time(11, 11)
        assert infos_arrivee.numero_vol == 'AF123'
        assert infos_depart.date_depart == date_depart

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


class SetAdresseTestCase(django.test.TestCase):
    DATA = {'adresse': u"Nouvelle adresse", 'code_postal': u"1234",
            'ville': u"neuf", 'pays': u"un pays"}

    def get_expected_adresse(self, rp):
        adresse = rp.get_adresse()
        return adresse._replace(**self.DATA)

    def post(self, inscription):
        session = self.client.session
        session['inscription_id'] = inscription.id
        session.save()
        self.client.post(reverse('set_adresse'), data=self.DATA)

    def test_sans_participant(self):
        i = InscriptionFactory(fermee=True, telephone='1234',
                               telecopieur='4567')
        i = InscriptionFermee.objects.get(id=i.id)
        self.post(i)
        i = InscriptionFermee.objects.get(id=i.id)
        self.assertEqual(i.get_adresse(),
                         self.get_expected_adresse(i))

    def test_avec_participant(self):
        i = InscriptionFactory(fermee=True)
        p = ParticipantFactory(inscription=i, telephone='1234',
                               telecopieur='4567')
        i = InscriptionFermee.objects.get(pk=i.id)
        self.post(i)
        p = Participant.objects.get(pk=p.id)
        self.assertEqual(p.get_adresse(),
                         self.get_expected_adresse(p))
