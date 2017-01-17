# -*- encoding: utf-8 -*-
import collections
import unittest
import html5lib
import datetime

import django.test
import django.http
import django.utils.http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import mail
from django.core.management import call_command


from auf.django.mailing.models import Enveloppe, ModeleCourriel

from ag.inscription.templatetags.inscription import adresse_email_region
from ag.reference.models import Etablissement, Pays
from ag.inscription.views import paypal_ipn
from ag.core.test_utils import find_input_by_id, InscriptionFactory, \
    find_input_by_name
import mock
from ag.gestion.models import (
    Participant,
    get_fonction_repr_universitaire)
from ag.inscription.forms import AccueilForm, RenseignementsPersonnelsForm, \
    TransportHebergementForm
from ag.inscription.models import Inscription, Invitation, \
    InvitationEnveloppe, PaypalInvoice, PaypalResponse, get_forfaits, Forfait
from ag.inscription.views import EtapesProcessus, inscriptions_terminees
from ag.tests import create_fixtures
from ag.gestion import consts

ETAPES_INSCRIPTION_TEST = (
    {
        "url_title": "accueil",
        "label": u"Accueil",
        "template": "accueil.html",
        "form_class": AccueilForm,
        "tab_visible": True,
    },
    {
        "url_title": "participant",
        "label": u"Renseignements personnels",
        "template": "participant.html",
        "form_class": RenseignementsPersonnelsForm,
        "tab_visible": True,
    },
    {
        "url_title": "transport-hebergement",
        "label": u"Transport et hébergement",
        "template": "transport_hebergement.html",
        "form_class": TransportHebergementForm,
        "tab_visible": False,
    },
)


# noinspection PyUnusedLocal
def url_etape(inscription, etape):
    return '/inscription/' + etape + '/'


def to_form_data(data):
    form_data = {}
    for key, value in data.iteritems():
        if type(value) == int:
            value = str(int)
        elif type(value) == datetime.date:
            value = value.isoformat()
        elif type(value) == bool:
            value = str(value)
        form_data[key] = value
    return form_data


# noinspection PyUnresolvedReferences
class InscriptionTestMixin(object):
    INSCRIPTION_TEST_DATA = {
        'participant': {
            'genre': u'M',
            'nom': u'nom test',
            'prenom': u'prenom test',
            'nationalite': u'nationalite test',
            'adresse': u'adresse test',
            'ville': u'ville test',
            'pays': u'pays test',
            'code_postal': u'12345',
            'telephone': u'7894561',
            'poste': u'poste test',
            'courriel': u'test@test.auf',
            'accompagnateur': False,
        },
        'transport-hebergement': {
            u'prise_en_charge_hebergement': False,
            u'prise_en_charge_transport': True,
        },
        'programmation': {
            u'programmation_soiree_9_mai': True,
            u'programmation_soiree_10_mai': True,
        },
    }

    def create_inscription(self, etapes_incluses, etablissement=None,
                           mandate=True):
        if not etablissement:  # par défaut, établissement du sud
            etablissement = Etablissement.objects.get(id=self.etablissement_id)
        if not Invitation.objects.count():
            call_command('generer_invitations_mandates')
        try:
            invitation = Invitation.objects.get(
                etablissement=etablissement,
                pour_mandate=mandate)
        except Invitation.DoesNotExist:
            if not mandate:
                enveloppe = Enveloppe(
                    modele=self.modele_courriel_accompagnateur)
                enveloppe.save()
                invitation = Invitation(pour_mandate=False)
                invitation.etablissement = Etablissement.objects \
                    .get(id=etablissement.id)
                invitation.save()
                invitation_enveloppe = InvitationEnveloppe()
                invitation_enveloppe.invitation = invitation
                invitation_enveloppe.enveloppe = enveloppe
                invitation_enveloppe.save()
            else:
                raise

        inscription = Inscription(invitation=invitation)
        for etape in etapes_incluses:
            inscription.__dict__.update(self.INSCRIPTION_TEST_DATA[etape])
        inscription.save()
        session = self.client.session
        session['inscription_id'] = inscription.id
        session.save()

        return inscription


class EtapesProcessusTestCase(unittest.TestCase):
    def setUp(self):
        self.etapes_processus = EtapesProcessus(
            donnees_etapes=ETAPES_INSCRIPTION_TEST)

    def test_etape_suivante_si_pas_derniere(self):
        e0 = self.etapes_processus[0]
        e1 = self.etapes_processus[1]
        assert self.etapes_processus.etape_suivante(e0) == e1

    def test_etape_suivante_si_derniere(self):
        e0 = self.etapes_processus[-1]
        assert self.etapes_processus.etape_suivante(e0) is None

    def test_etape_par_url(self):
        etape = self.etapes_processus.etape_par_url('participant')
        assert etape.url_title == 'participant'

    def test_derniere_visible(self):
        etapes = EtapesProcessus(donnees_etapes=(
            {'tab_visible': True},
            {'tab_visible': False}))
        assert etapes[0].est_derniere_visible()

    def test_pas_derniere_visible(self):
        etapes = EtapesProcessus(donnees_etapes=(
            {'tab_visible': True},
            {'tab_visible': True}))
        assert not etapes[0].est_derniere_visible()

    def test_numerotation(self):
        etapes = EtapesProcessus(donnees_etapes=(
            {'tab_visible': True},
            {'tab_visible': True}))
        assert [e.n for e in etapes] == [0, 1]

    def test_derniere(self):
        assert self.etapes_processus[-1].est_derniere()

    def test_pas_derniere(self):
        assert not self.etapes_processus[-2].est_derniere()


# noinspection PyUnresolvedReferences
@mock.patch('ag.inscription.views.inscriptions_terminees', lambda: False)
class TestsInscription(django.test.TestCase, InscriptionTestMixin):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.forfaits = get_forfaits()

    def tearDown(self):
        self.client.logout()

    def test_accueil_non_mandate(self):
        inscription = self.create_inscription([], mandate=False)
        response = self.client.get(url_etape(inscription, 'accueil'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        assert (find_input_by_name(tree, 'identite_accompagnateur_confirmee')
                is not None)
        assert find_input_by_name(tree, 'atteste_pha') is None

    def test_accueil_mandate(self):
        inscription = self.create_inscription([], mandate=True)
        response = self.client.get(url_etape(inscription, 'accueil'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        assert find_input_by_name(tree, 'atteste_pha') is not None
        assert (find_input_by_name(tree, 'identite_accompagnateur_confirmee')
                is None)

    def test_debut_processus(self):
        inscription = self.create_inscription([])
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertContains(response,
                            u'représentent officiellement un établissement')
        response = self.client.post(url_etape(inscription, 'accueil'),
                                    data={
                                        'atteste_pha': u'P',
                                        'conditions_acceptees': u'on',
                                    })
        self.assertRedirects(
            response,
            reverse('processus_inscription',
                    kwargs={'url_title': 'participant'}))
        response = self.client.get(url_etape(inscription,
                                             'participant'))
        self.assertEqual(response.status_code, 200)
        rp_data = to_form_data(
            self.INSCRIPTION_TEST_DATA['participant'])
        response = self.client.post(
            url_etape(inscription, 'participant'), rp_data)
        self.assertRedirects(
            response, reverse('processus_inscription',
                              kwargs={'url_title': 'programmation'}))
        inscription = Inscription.objects.all()[0]
        self.assertEquals(inscription.genre, rp_data['genre'])
        self.assertEquals(inscription.nom, rp_data['nom'].upper())
        self.assertEquals(inscription.prenom, rp_data['prenom'])

    def ajouter_accompagnateur(self, inscription):
        inscription.accompagnateur = True
        inscription.accompagnateur_genre = 'M'
        inscription.accompagnateur_nom = 'Accomp'
        inscription.accompagnateur_prenom = 'agnateur'
        inscription.save()

    def test_prise_en_charge_titulaire_sud_accompagne(self):
        # on propose la prise en charge aux mandatés du Sud avec accompagnateurs
        inscription = self.create_inscription(('participant',))
        self.ajouter_accompagnateur(inscription)
        response = self.client.get(
            url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"),
            None)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_transport_0"), None)
        th_data = to_form_data(
            self.INSCRIPTION_TEST_DATA['transport-hebergement'])
        response = self.client.post(
            url_etape(inscription, 'transport-hebergement'), th_data)
        self.assertRedirects(response,
                             reverse('processus_inscription',
                                     kwargs={'url_title': 'apercu'}))

    def test_prise_en_charge_associe_sud(self):
        # on propose la prise en charge Hébergement aux mandatés
        # d'établissements associés du Sud mais pas la prise en charge
        # Transport
        etablissement_associe = Etablissement.objects.get(
            id=self.etablissement_sud_associe_id)
        inscription = self.create_inscription(
            ('participant',), etablissement=etablissement_associe)
        response = self.client.get(
            url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)

        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)
        self.assertEqual(
            find_input_by_id(tree, "id_prise_en_charge_transport_0"), None)
        th_data = to_form_data(
            self.INSCRIPTION_TEST_DATA['transport-hebergement'])
        response = self.client.post(
            url_etape(inscription, 'transport-hebergement'), th_data)
        self.assertRedirects(response,
                             reverse('processus_inscription',
                                     kwargs={'url_title': 'apercu'}))

    def test_make_paypal_invoice(self):
        # ModeleCourriel.objects.create(code='recu_ok', sujet=u"a", corps=u"b",
        #                               html=False)
        i = self.create_inscription(['participant', 'transport-hebergement',
                                     'programmation'])
        nb_mail = len(mail.outbox)
        response = self.client.post(reverse('make_paypal_invoice'))
        assert response.status_code == 200
        i = Inscription.objects.get(id=i.id)
        assert i.fermee
        invoice = PaypalInvoice.objects.get(inscription=i)
        assert invoice.montant == i.get_solde_a_payer()
        # un mail au participant et un au service et un au bureau régional
        assert len(mail.outbox) == nb_mail + 3

    def test_transport_hebergement(self):
        inscription = self.create_inscription(('participant',))
        response = self.client.get(
            url_etape(inscription, 'transport-hebergement'))
        # on propose la prise en charge aux mandatés du Sud sans accompagnateurs
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_transport_0"), None)

        th_data = to_form_data(
            self.INSCRIPTION_TEST_DATA['transport-hebergement'])
        response = self.client.post(
            url_etape(inscription, 'transport-hebergement'), th_data)
        self.assertRedirects(response,
                             reverse('processus_inscription',
                                     kwargs={'url_title': 'apercu'}))
        # on ne propose pas la prise en charge aux accompagnateurs du Sud
        inscription = self.create_inscription(('participant',),
                                              mandate=False)
        response = self.client.get(
            url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)
        # on ne propose pas la prise en charge aux mandatés du Nord
        inscription = self.create_inscription(
            ('participant',),
            mandate=True,
            etablissement=Etablissement.objects.get(
                id=self.etablissement_nord_id))
        response = self.client.get(
            url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)

    def test_programmation(self):
        inscription = self.create_inscription(
            ('participant', 'transport-hebergement'))
        response = self.client.get(
            url_etape(inscription, 'transport-hebergement'))
        self.assertNotContains(
            response,
            'id="id_programmation_soiree_interconsulaire_invite"')
        self.assertNotContains(response, 'id="id_programmation_gala_invite"')
        inscription.accompagnateur = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'programmation'))
        self.assertContains(
            response,
            'id="id_programmation_soiree_9_mai_invite"')
        self.assertContains(response, 'id="id_programmation_gala_invite"')

    def test_post_programmation_sud(self):
        inscription = self.create_inscription(
            ('participant', 'transport-hebergement'))
        response = self.client.post(url_etape(inscription, 'programmation'),
                                    data=to_form_data(
                                        self.INSCRIPTION_TEST_DATA[
                                            'programmation']))
        self.assertRedirects(
            response, reverse('processus_inscription',
                              kwargs={
                                  'url_title': 'transport-hebergement'}))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertEquals(inscription.programmation_soiree_9_mai, True)
        self.assertEquals(inscription.programmation_soiree_9_mai_invite, False)
        self.assertEquals(inscription.programmation_soiree_10_mai,
                          True)
        self.assertEquals(
            inscription.programmation_soiree_10_mai_invite, False)

    def test_post_programmation_nord_etape_suivante_apercu(self):
        etablissement_nord = Etablissement.objects.get(
            pk=self.etablissement_nord_id)
        inscription = self.create_inscription(
            ('participant', 'transport-hebergement'),
            etablissement=etablissement_nord
        )
        response = self.client.post(url_etape(inscription, 'programmation'),
                                    data=to_form_data(
                                        self.INSCRIPTION_TEST_DATA[
                                            'programmation']))
        self.assertRedirects(
            response, reverse('processus_inscription',
                              kwargs={
                                  'url_title': 'apercu'}))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertEquals(inscription.programmation_soiree_9_mai, True)
        self.assertEquals(inscription.programmation_soiree_9_mai_invite, False)
        self.assertEquals(inscription.programmation_soiree_10_mai,
                          True)
        self.assertEquals(
            inscription.programmation_soiree_10_mai_invite, False)

    def test_apercu_chambre_double(self):
        inscription = self.create_inscription(('participant',
                                               'transport-hebergement',
                                               'programmation', ))
        inscription.accompagnateur = True
        inscription.prise_en_charge_hebergement = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'apercu'))
        self.assertContains(response, u"supplément occupation double")
        self.assertContains(response, Forfait.objects.get(
            code=consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE).affiche())

    def test_apercu_pas_de_supplement(self):
        inscription = self.create_inscription(('participant',
                                               'transport-hebergement',
                                               'programmation', ))
        response = self.client.get(url_etape(inscription, 'apercu'))
        self.assertNotContains(response, u"supplément")

    def test_apercu_modifier_redirect_participant(self):
        inscription = self.create_inscription(('participant',
                                               'transport-hebergement',
                                               'programmation', ))
        response = self.client.post(url_etape(inscription, 'apercu'),
                                    data={u'modifier': u'on'})
        self.assertRedirects(
            response,
            reverse('processus_inscription',
                    kwargs={'url_title': 'participant'}))

    def test_apercu_confirmer_redirect_dossier(self):
        inscription = self.create_inscription(('participant',
                                               'transport-hebergement',
                                               'programmation', ))
        outbox_len = len(mail.outbox)
        response = self.client.post(url_etape(inscription, 'apercu'),
                                    data={u'confirmer': u'on'})
        self.assertRedirects(
            response,
            reverse('dossier_inscription'))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertTrue(inscription.fermee)
        self.assertTrue(inscription.prise_en_charge_transport)
        self.assertEqual(outbox_len + 3, len(mail.outbox))

    def test_confirmation_prise_en_charge_interdite(self):
        inscription = self.create_inscription(
            ('participant',
             'transport-hebergement',
             'programmation', ),
            etablissement=Etablissement.objects.get(
                id=self.etablissement_nord_id))
        response = self.client.post(url_etape(inscription, 'apercu'),
                                    data={u'confirmer': u'on'})
        self.assertRedirects(
            response, reverse('dossier_inscription'))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertTrue(inscription.fermee)
        self.assertFalse(inscription.prise_en_charge_hebergement)
        self.assertFalse(inscription.prise_en_charge_transport)

    def test_liste_frais(self):
        inscription = Inscription()
        self.assertEquals(inscription.get_montant_total(),
                          inscription.get_frais_inscription())
        self.assertEquals(inscription.get_frais_inscription(),
                          self.forfaits[consts.CODE_FRAIS_INSCRIPTION].montant)
        inscription.accompagnateur = True
        liste = frozenset(inscription.get_liste_codes_frais())
        self.assertEqual(liste, frozenset((consts.CODE_FRAIS_INSCRIPTION,)))
        self.assertEquals(
            inscription.get_frais_inscription(),
            self.forfaits[consts.CODE_FRAIS_INSCRIPTION].montant)

    def test_commande_generer_invitation_mandates(self):
        call_command('generer_invitations_mandates')
        # il y a trois établissements mais l'un d'entre eux n'a pas d'adresse
        # de courriel et ne peut donc pas recevoir d'invitation
        self.assertEquals(Invitation.objects.count(),
                          self.total_etablissements_membres_avec_courriel)
        invitation = Invitation.objects.get(
            etablissement__id=self.etablissement_id)
        enveloppe = invitation.invitationenveloppe_set.all()[0].enveloppe
        self.assertEquals(enveloppe.get_adresse(),
                          invitation.etablissement.responsable_courriel)
        self.assertNotEqual(invitation.jeton, None)
        self.assertNotEqual(invitation.jeton, "")

    def test_commande_generer_rappels(self):
        call_command('generer_invitations_mandates')
        call_command('envoyer_invitations')
        length_of_outbox_before = len(mail.outbox)
        inscription = self.create_inscription(['participant'])
        inscription.fermee = True
        inscription.save()
        participant = Participant()
        participant.nom = 'Inscrit manuellement'
        participant.prenom = 'Inscrit manuellement'
        participant.courriel = 'abc@ccc.com'
        participant.fonction = get_fonction_repr_universitaire()
        participant.etablissement = Etablissement.objects.get(
            id=self.etablissement_nord_id)
        participant.save()

        call_command('generer_rappels', destinataires='mandates')
        modele_rappel = ModeleCourriel.objects.get(code='mand_rel')
        enveloppes = Enveloppe.objects.filter(modele=modele_rappel)
        self.assertEqual(len(enveloppes),
                         self.total_etablissements_membres_avec_courriel - 2)
        for enveloppe in enveloppes:
            invitation = enveloppe.invitationenveloppe.invitation
            self.assertEqual(Participant.objects.filter(
                etablissement=invitation.etablissement).count(), 0)

        call_command('envoyer_invitations')
        self.assertEqual(len(mail.outbox), length_of_outbox_before + 1)

    def test_premiere_connexion(self):
        call_command('generer_invitations_mandates')
        invitation = Invitation.objects.get(
            etablissement__id=self.etablissement_id,
            pour_mandate=True)
        response = self.client.get('/inscription/connexion/' + invitation.jeton)
        inscription = Inscription.objects.get(invitation=invitation)
        self.assertRedirects(response, url_etape(inscription, 'accueil'))
        self.assertTrue(inscription.numero_dossier)

    def test_inscription_fermee(self):
        inscription = self.create_inscription([])
        inscription.fermee = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertRedirects(
            response, reverse('dossier_inscription'))

    def test_facturation(self):
        inscription = self.create_inscription(['participant',
                                               'transport-hebergement', ])
        total_attendu = self.forfaits[consts.CODE_FRAIS_INSCRIPTION].montant
        self.assertEqual(inscription.get_montant_total(),
                         total_attendu)


class EnvoiInvitationsTestCase(django.test.TestCase):
    def setUp(self):
        create_fixtures(self)

    # noinspection PyUnresolvedReferences
    def test_commande_envoi_courriels(self):
        call_command('generer_invitations_mandates')
        call_command('envoyer_invitations')
        self.assertEqual(len(mail.outbox),
                         self.total_etablissements_membres_avec_courriel)

        from_emails = set(m.from_email for m in mail.outbox)
        region_codes = set(e.region.code for e in
                           self.etablissements_avec_courriel)
        assert from_emails == set(
            "AUF AG2017 <{}>".format(adresse_email_region(code))
            for code in region_codes)


@mock.patch('ag.inscription.views.inscriptions_terminees', lambda: True)
class FinInscriptionsTestCase(django.test.TestCase, InscriptionTestMixin):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)

    def tearDown(self):
        self.client.logout()

    def test_non_inscrit_1er_acces(self):
        call_command('generer_invitations_mandates')
        invitation = Invitation.objects.get(
            etablissement__id=self.etablissement_id,
            pour_mandate=True)
        response = self.client.get('/inscription/connexion/' + invitation.jeton)
        self.assertRedirects(response, reverse('inscriptions_terminees'))

    def test_inscription_non_fermee(self):
        inscription = self.create_inscription(['participant'])
        response = self.client.get('/inscription/connexion/' +
                                   inscription.invitation.jeton)
        self.assertRedirects(response, reverse('inscriptions_terminees'))

    def test_inscrit(self):
        inscription = self.create_inscription(['participant'])
        inscription.fermee = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertRedirects(response, reverse('dossier_inscription'))

    def test_get_inscription_representant_etablissement(self):
        im = self.create_inscription([])
        inm = self.create_inscription([], mandate=False)
        assert inm.get_inscription_representant_etablissement() == im
        assert im.get_inscription_representant_etablissement() == im


class FakeDate(datetime.date):
    """Une fausse date qui peut être mockée.
    Voir http://williamjohnbert.com/2011/07/
    how-to-unit-testing-in-django-with-mocking-and-patching/"""

    def __new__(cls, *args, **kwargs):
        return datetime.date.__new__(datetime.date, *args, **kwargs)


@mock.patch('ag.inscription.views.datetime.date', FakeDate)
def test_inscription_terminee():
    FakeDate.today = classmethod(
        lambda cls: settings.DATE_FERMETURE_INSCRIPTIONS +
        datetime.timedelta(days=1))
    assert (inscriptions_terminees())
    FakeDate.today = classmethod(
        lambda cls: settings.DATE_FERMETURE_INSCRIPTIONS -
        datetime.timedelta(days=1))
    assert (not inscriptions_terminees())


class PreremplirTest(unittest.TestCase):

    def setUp(self):
        p = Pays(nom=u"pppp")
        self.etablissement = Etablissement(
            nom=u"eeee", adresse=u"adr", ville=u"laville",
            code_postal=u"60240", pays=p, telephone=u"123123123",
            responsable_nom=u"rn", responsable_prenom=u"rp",
            responsable_courriel=u"rc", responsable_fonction=u"rf",
            responsable_genre=u"F")

    def make_donnees_preremplir(self, pour_mandate, nom=None, prenom=None,
                                pha='P', courriel=None):
        invitation = Invitation(
            pour_mandate=pour_mandate,
            etablissement=self.etablissement,
            courriel=courriel or self.etablissement.responsable_courriel,
            nom=nom, prenom=prenom)
        inscription = Inscription(invitation=invitation, atteste_pha=pha)
        return inscription.get_donnees_preremplir()

    def test_pas_pour_mandate_renseignements_personnels_non_remplis(self):
        d = self.make_donnees_preremplir(pour_mandate=False, nom="nom_invite",
                                         prenom="prenom_invite",
                                         courriel="courriel_invite")
        assert d['nom'] == "nom_invite"
        assert d['prenom'] == "prenom_invite"
        assert d['courriel'] == 'courriel_invite'
        assert 'poste' not in d
        assert 'genre' not in d

    def test_pour_mandate_renseignements_personnels_remplis_si_pha(self):
        d = self.make_donnees_preremplir(pour_mandate=True)
        e = self.etablissement
        assert d['nom'] == e.responsable_nom
        assert d['prenom'] == e.responsable_prenom
        assert d['poste'] == e.responsable_fonction
        assert d['genre'] == e.responsable_genre
        assert d['courriel'] == e.responsable_courriel

    def test_pour_mandate_renseignements_personnels_pas_remplis_si_pas_pha(self):
        d = self.make_donnees_preremplir(pour_mandate=True, pha='R')
        assert 'nom' not in d
        assert 'prenom' not in d
        assert 'poste' not in d
        assert 'genre' not in d
        assert 'courriel' not in d

    def test_champs_etablissement_copies(self):
        d = self.make_donnees_preremplir(False)
        e = self.etablissement
        assert d['ville'] == e.ville
        assert d['pays'] == e.pays.nom
        assert d['adresse'].startswith(e.nom)
        assert d['adresse'].endswith(e.adresse)
        assert d['code_postal'] == e.code_postal
        assert d['telephone'] == e.telephone


class PaypalCancelTests(django.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super(PaypalCancelTests, cls).setUpClass()
        inscription = InscriptionFactory()
        cls.invoice = PaypalInvoice.objects.create(inscription=inscription,
                                                   montant=100)

    def setUp(self):
        url = reverse('paypal_cancel', args=(str(self.invoice.invoice_uid),))
        self.response = self.client.get(url)

    def test_status_code_redirect(self):
        assert self.response.status_code == 302

    def test_cancel_in_database(self):
        responses = PaypalResponse.objects.filter(
            type_reponse="CAN", invoice_uid=self.invoice.invoice_uid)
        assert responses.count() == 1


FakeRequest = collections.namedtuple('FakeRequest', ('body', 'POST', ))


@mock.patch('ag.inscription.views.is_ipn_valid', lambda x: (True, 'val_resp'))
class PaypalIPNTests(django.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super(PaypalIPNTests, cls).setUpClass()
        inscription = InscriptionFactory()
        cls.invoice = PaypalInvoice.objects.create(inscription=inscription,
                                                   montant=100)
        body = django.utils.http.urlencode({
            "mc_gross": "150.0",
            "mc_currency": "EUR",
            "invoice": str(cls.invoice.invoice_uid),
            "payment_date": "12:13:14 Oct. 10, 2016 PST",
            "payment_status": "ACCEPTED",
            "pending_reason": "",
            "txn_id": "the_txn_id",
        })
        patcher = mock.patch('ag.inscription.views.is_ipn_valid')
        fn_mock = patcher.start()
        try:
            fn_mock.return_value = (True, 'val_resp')
            # on ne peut pas utiliser client.post ici car la propriété
            # request.body n'est alors pas accessible dans la vue
            cls.response = paypal_ipn(
                FakeRequest(body=body, POST=django.http.QueryDict(body)))
        finally:
            patcher.stop()

    def test_paypal_response_created_in_db(self):
        assert PaypalResponse.objects.filter(
            type_reponse='IPN',
            invoice_uid=self.invoice.invoice_uid).count() == 1

    def test_paypal_response_txn_id_in_db(self):
        assert PaypalResponse.objects.filter(
            type_reponse='IPN',
            invoice_uid=self.invoice.invoice_uid)[0].txn_id == "the_txn_id"

    def test_paypal_validated_in_db(self):
        assert PaypalResponse.objects.filter(
            type_reponse='IPN',
            invoice_uid=self.invoice.invoice_uid)[0].validated


class InscriptionFonctionsPaypalTestCase(django.test.TestCase):
    def setUp(self):
        i = self.i = InscriptionFactory()  # type: Inscription
        invoice = PaypalInvoice.objects.create(inscription=i, montant=150)
        PaypalResponse.objects.create(inscription=i, type_reponse="IPN",
                                      montant=150, statut="Completed",
                                      invoice_uid=invoice.invoice_uid,
                                      validated=True)
        PaypalResponse.objects.create(inscription=i, statut="Completed",
                                      type_reponse="PDT", montant=150,
                                      invoice_uid=invoice.invoice_uid,
                                      validated=True)

    def test_unique_responses(self):
        assert len(self.i.get_unique_paypal_responses()) == 1

    def test_total_compte_une_fois(self):
        # Il peut y avoir plusieurs confirmations pour la même transaction
        # (IPN/PDT), mais quand on fait le total on ne doit compter qu'une fois
        assert self.i.paiement_paypal_total() == 150

    def test_paiement_paypal_ok(self):
        assert self.i.paiement_paypal_ok()

    def test_paiement_paypal_not_ok(self):
        PaypalResponse.objects.update(validated=False)
        assert not self.i.paiement_paypal_ok()

    def test_total_0_if_not_validated(self):
        PaypalResponse.objects.update(validated=False)
        assert self.i.paiement_paypal_total() == 0
