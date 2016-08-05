# -*- encoding: utf-8 -*-
import html5lib
import datetime

from auf.django.mailing.models import Enveloppe, ModeleCourriel
from auf.django.references.models import Etablissement

from ag.core.test_utils import find_input_by_id
import mock
from ag.gestion.models import Participant, StatutParticipant
from ag.inscription.forms import AccueilForm, RenseignementsPersonnelsForm, \
    TransportHebergementForm
from ag.inscription.models import Inscription, Invitation, \
    infos_montant_par_code, InvitationEnveloppe
from ag.inscription.views import EtapesProcessus, inscriptions_terminees
from ag.tests import create_fixtures
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase
from django.core.management import call_command

ETAPES_INSCRIPTION_TEST = (
        {
        "n": 0,
        "url_title": "accueil",
        "label": u"Accueil",
        "template": "accueil.html",
        "form_class": AccueilForm,
        "tab_visible": True,
        },
        {
        "n": 1,
        "url_title": "renseignements-personnels",
        "label": u"Renseignements personnels",
        "template": "renseignements_personnels.html",
        "form_class": RenseignementsPersonnelsForm,
        "tab_visible": True,
        },
        {
        "n": 2,
        "url_title": "transport-hebergement",
        "label": u"Transport et hébergement",
        "template": "transport_hebergement.html",
        "form_class": TransportHebergementForm,
        "tab_visible": False,
        },
)


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


class InscriptionTestMixin(object):
    INSCRIPTION_TEST_DATA = {
        'renseignements-personnels' : {
            'genre': u'M',
            'nom' : u'nom test',
            'prenom' : u'prenom test',
            'nationalite' : u'nationalite test',
            'adresse' : u'adresse test',
            'ville' : u'ville test',
            'pays' : u'pays test',
            'code_postal' : u'12345',
            'telephone' : u'7894561',
            'poste' : u'poste test',
            'courriel': u'test@test.auf',
            'accompagnateur': False,
            },
        'transport-hebergement': {
            u'arrivee_compagnie': u'Air Test',
            u'arrivee_date': datetime.date(2013,05,06),
            u'depart_heure': datetime.time(9,30),
            u'depart_vol': u'TST',
            u'depart_compagnie': u'Air Test',
            u'arrivee_heure': datetime.time(9,30),
            u'depart_date': datetime.date(2013,05,10),
            u'arrivee_vol': u'arr',
            u'prise_en_charge_hebergement': False,
            u'prise_en_charge_transport': True,
            u'date_arrivee_hotel': datetime.date(2013,05,06),
            u'date_depart_hotel': datetime.date(2013,05,8),
            u'date_naissance': datetime.date(1965,03,15),
            },
        'programmation' : {
            u'programmation_soiree_unesp': True,
            u'programmation_soiree_interconsulaire': True,
            },
        'paiement': {
            u'paiement': u'VB',
            }
    }

    def create_inscription(self, etapes_incluses, etablissement=None, mandate=True):
        if not etablissement:
            etablissement = Etablissement.objects.get(id=self.etablissement_id)
        if not Invitation.objects.count():
            call_command('generer_invitations_mandates')
        try:
            invitation = Invitation.objects.get(
                etablissement=etablissement,
                pour_mandate=mandate)
        except Invitation.DoesNotExist:
            if not mandate:
                enveloppe = Enveloppe(modele=self.modele_courriel_accompagnateur)
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


@mock.patch('ag.inscription.views.inscriptions_terminees', lambda: False)
class TestsInscription(TestCase, InscriptionTestMixin):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)

    def tearDown(self):
        self.client.logout()

    def test_etapes_processus(self):
        etapes_processus = EtapesProcessus(donnees_etapes=ETAPES_INSCRIPTION_TEST)
        etape = etapes_processus.etape_par_url('renseignements-personnels')
        self.assertEqual(etape, etapes_processus[1])
        self.assertTrue(etape.est_derniere_visible())
        self.assertFalse(etape.est_derniere())
        derniere_etape = etapes_processus.etape_suivante(etape)
        self.assertEqual(derniere_etape, etapes_processus[2])
        self.assertTrue(derniere_etape.est_derniere())
        self.assertEqual(etapes_processus.etape_suivante(derniere_etape), None)

    def test_accueil_non_mandate(self):
        inscription = self.create_inscription([], mandate=False)
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertContains(response, u'accompagnateurs issus du même')

    def test_debut_processus(self):
        inscription = self.create_inscription([])
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertContains(response, u'représentent officiellement un établissement')
        response = self.client.post(url_etape(inscription, 'accueil'),
            data={
                'identite_confirmee' : u'on',
                'conditions_acceptees' : u'on',
            })
        self.assertRedirects(response,
            reverse('processus_inscription',
            kwargs={ 'url_title' : 'renseignements-personnels' }))
        response = self.client.get(url_etape(inscription,
            'renseignements-personnels'))
        self.assertEqual(response.status_code, 200)
        rp_data = to_form_data(self.INSCRIPTION_TEST_DATA['renseignements-personnels'])
        response = self.client.post(url_etape(inscription, 'renseignements-personnels'), rp_data)
        self.assertRedirects(response, reverse('processus_inscription',
            kwargs={ 'url_title' : 'programmation' }))
        inscription = Inscription.objects.all()[0]
        self.assertEquals(inscription.genre, rp_data['genre'])
        self.assertEquals(inscription.nom, rp_data['nom'].upper())
        self.assertEquals(inscription.prenom, rp_data['prenom'])
        self.assertEquals(inscription.nationalite, rp_data['nationalite'])

    def ajouter_accompagnateur(self, inscription):
        inscription.accompagnateur = True
        inscription.accompagnateur_genre = 'M'
        inscription.accompagnateur_nom = 'Accomp'
        inscription.accompagnateur_prenom = 'agnateur'
        inscription.save()

    def test_prise_en_charge_titulaire_sud_accompagne(self):
        # on propose la prise en charge aux mandatés du Sud avec accompagnateurs
        inscription = self.create_inscription(('renseignements-personnels',))
        self.ajouter_accompagnateur(inscription)
        response = self.client.get(url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"),
            None)
        self.assertContains(response, u"pas prendre en charge l'hébergement")
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_transport_0"), None)
        self.assertContains(response, u"pas prendre en charge le transport")
        th_data = to_form_data(self.INSCRIPTION_TEST_DATA['transport-hebergement'])
        response = self.client.post(
            url_etape(inscription, 'transport-hebergement'), th_data)
        self.assertRedirects(response,
            reverse('processus_inscription', kwargs={ 'url_title' : 'paiement' }))

    def test_prise_en_charge_associe_sud(self):
        # on propose la prise en charge Hébergement aux mandatés
        # d'établissements associés du Sud mais pas la prise en charge
        # Transport
        etablissement_associe = Etablissement.objects.get(id=self.etablissement_sud_associe_id)
        inscription = self.create_inscription(('renseignements-personnels',),
            etablissement=etablissement_associe)
        response = self.client.get(url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)

        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)
        self.assertEqual(
            find_input_by_id(tree, "id_prise_en_charge_transport_0"), None)
        th_data = to_form_data(self.INSCRIPTION_TEST_DATA['transport-hebergement'])
        response = self.client.post(
            url_etape(inscription, 'transport-hebergement'), th_data)
        self.assertRedirects(response,
            reverse('processus_inscription', kwargs={ 'url_title' : 'paiement' }))

    def test_transport_hebergement(self):
        inscription = self.create_inscription(('renseignements-personnels',))
        response = self.client.get(url_etape(inscription, 'transport-hebergement'))
        # on propose la prise en charge aux mandatés du Sud sans accompagnateurs
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)
        self.assertNotEqual(
            find_input_by_id(tree, "id_prise_en_charge_transport_0"), None)

        th_data = to_form_data(self.INSCRIPTION_TEST_DATA['transport-hebergement'])
        response = self.client.post(
            url_etape(inscription, 'transport-hebergement'), th_data)
        self.assertRedirects(response,
            reverse('processus_inscription', kwargs={ 'url_title' : 'paiement' }))
        # on ne propose pas la prise en charge aux accompagnateurs du Sud
        inscription = self.create_inscription(('renseignements-personnels',),
            mandate=False)
        response = self.client.get(url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)
        # on ne propose pas la prise en charge aux mandatés du Nord
        inscription = self.create_inscription(('renseignements-personnels',),
            mandate=True,
            etablissement=Etablissement.objects.get(id=self.etablissement_nord_id))
        response = self.client.get(url_etape(inscription, 'transport-hebergement'))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        self.assertEqual(
            find_input_by_id(tree, "id_prise_en_charge_hebergement_0"), None)

    def test_programmation(self):
        inscription = self.create_inscription(('renseignements-personnels', 'transport-hebergement'))
        response = self.client.get(url_etape(inscription, 'transport-hebergement'))
        self.assertNotContains(response, 'id="id_programmation_soiree_interconsulaire_invite"')
        self.assertNotContains(response, 'id="id_programmation_gala_invite"')
        inscription.accompagnateur = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'programmation'))
        self.assertContains(response, 'id="id_programmation_soiree_interconsulaire_invite"')
        self.assertContains(response, 'id="id_programmation_gala_invite"')
        response = self.client.post(url_etape(inscription, 'programmation'),
            data=to_form_data(self.INSCRIPTION_TEST_DATA['programmation']))
        self.assertRedirects(response, reverse('processus_inscription',
            kwargs={ 'url_title' : 'transport-hebergement' }))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertEquals(inscription.programmation_soiree_unesp, True)
        self.assertEquals(inscription.programmation_soiree_unesp_invite, False)
        self.assertEquals(inscription.programmation_soiree_interconsulaire, True)
        self.assertEquals(inscription.programmation_soiree_interconsulaire_invite, False)

    def test_apercu_chambre_double(self):
        inscription = self.create_inscription(('renseignements-personnels', 'transport-hebergement', 'programmation', 'paiement'))
        inscription.accompagnateur = True
        inscription.prise_en_charge_hebergement = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'apercu'))
        self.assertContains(response, u"supplément pour invité")

    def test_apercu(self):
        inscription = self.create_inscription(('renseignements-personnels', 'transport-hebergement', 'programmation', 'paiement'))
        response = self.client.get(url_etape(inscription, 'apercu'))
        self.assertNotContains(response, u"supplément pour invité")
        self.assertContains(response, u"Soirée organisée par l'UNESP du 7 mai 2013")
        self.assertNotContains(response, u"Rencontre avec les universités membres du 10 mai 2013")
        response = self.client.post(url_etape(inscription, 'apercu'), data={u'modifier':u'on'})
        self.assertRedirects(response, reverse('processus_inscription',
            kwargs = { 'url_title': 'renseignements-personnels' }))
        response = self.client.post(url_etape(inscription, 'apercu'), data={u'confirmer':u'on'})
        self.assertRedirects(response, reverse('processus_inscription',
            kwargs = { 'url_title': 'confirmation' }))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertTrue(inscription.fermee)
        self.assertTrue(inscription.prise_en_charge_transport)

    def test_confirmation_prise_en_charge_interdite(self):
        inscription = self.create_inscription(('renseignements-personnels',
            'transport-hebergement', 'programmation', 'paiement'),
            etablissement=Etablissement.objects.get(id=self.etablissement_nord_id))
        response = self.client.post(url_etape(inscription, 'apercu'), data={u'confirmer':u'on'})
        self.assertRedirects(response, reverse('processus_inscription',
            kwargs = { 'url_title': 'confirmation' }))
        inscription = Inscription.objects.get(id=inscription.id)
        self.assertTrue(inscription.fermee)
        self.assertFalse(inscription.prise_en_charge_hebergement)
        self.assertFalse(inscription.prise_en_charge_transport)



    def test_liste_frais(self):
        inscription = Inscription()
        self.assertEquals(inscription.get_montant_total(), inscription.get_frais_inscription())
        self.assertEquals(inscription.get_frais_inscription(), infos_montant_par_code('frais_inscription').montant)
        inscription.accompagnateur = True
        liste = frozenset(inscription.get_liste_codes_frais())
        self.assertEqual(liste, frozenset(('frais_inscription', 'frais_inscription_invite' )))
        self.assertEquals(inscription.get_frais_inscription(),
            infos_montant_par_code('frais_inscription').montant + infos_montant_par_code('frais_inscription_invite').montant)

    def test_commande_generer_invitation_mandates(self):
        call_command('generer_invitations_mandates')
        # il y a trois établissements mais l'un d'entre eux n'a pas d'adresse
        # de courriel et ne peut donc pas recevoir d'invitation
        self.assertEquals(Invitation.objects.count(),
                          self.total_etablissements_membres_avec_courriel)
        invitation = Invitation.objects.get(etablissement__id=self.etablissement_id)
        enveloppe = invitation.invitationenveloppe_set.all()[0].enveloppe
        self.assertEquals(enveloppe.get_adresse(), invitation.etablissement.responsable_courriel)
        self.assertNotEqual(invitation.jeton, None)
        self.assertNotEqual(invitation.jeton, "")

    def test_commande_envoi_courriels(self):
        call_command('generer_invitations_mandates')
        call_command('envoyer_invitations')
        self.assertEqual(len(mail.outbox),
            self.total_etablissements_membres_avec_courriel)

    def test_commande_generer_rappels(self):
        call_command('generer_invitations_mandates')
        call_command('envoyer_invitations')
        length_of_outbox_before = len (mail.outbox)
        inscription = self.create_inscription(['renseignements-personnels'])
        inscription.fermee = True
        inscription.save()
        participant = Participant()
        participant.nom = 'Inscrit manuellement'
        participant.prenom = 'Inscrit manuellement'
        participant.courriel = 'abc@ccc.com'
        participant.type_institution = 'E'
        participant.etablissement = Etablissement.objects.get(id=self.etablissement_nord_id)
        participant.statut = StatutParticipant.objects.get(code='repr_tit')
        participant.save()

        call_command('generer_rappels', destinataires='mandates')
        modele_rappel = ModeleCourriel.objects.get(code='mand_rel')
        enveloppes = Enveloppe.objects.filter(modele=modele_rappel)
        self.assertEqual(len(enveloppes),
            self.total_etablissements_membres_avec_courriel - 2)
        for enveloppe in enveloppes:
            invitation = enveloppe.invitationenveloppe.invitation
            self.assertEqual(Participant.objects.filter(etablissement=invitation.etablissement).count(), 0)

        call_command('envoyer_invitations')
        self.assertEqual(len(mail.outbox), length_of_outbox_before + 1)

    def test_premiere_connexion(self):
        call_command('generer_invitations_mandates')
        invitation = Invitation.objects.get(etablissement__id=self.etablissement_id,
            pour_mandate=True)
        response = self.client.get('/inscription/connexion/' + invitation.jeton)
        inscription = Inscription.objects.get(invitation=invitation)
        self.assertRedirects(response, url_etape(inscription, 'accueil') )
        self.assertEqual(inscription.adresse, invitation.etablissement.nom + "\n" + invitation.etablissement.adresse)
        self.assertEqual(inscription.ville, invitation.etablissement.ville)
        self.assertEqual(inscription.code_postal, invitation.etablissement.code_postal)
        self.assertEqual(inscription.pays, invitation.etablissement.pays.nom)

    def test_inscription_fermee(self):
        inscription = self.create_inscription([])
        inscription.fermee = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertRedirects(response, reverse('processus_inscription',
            kwargs = { 'url_title' : 'confirmation' }))

    def test_ajout_invitations(self):
        inscription = self.create_inscription([])
        inscription.fermee = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'confirmation'))
        self.assertContains(response, u'<textarea id="liste_adresses"')
        nombre_invitations_avant = Invitation.objects.count()
        ADRESSE_TEST = 'adresse1@test.org'
        response = self.client.post(reverse('ajout_invitations'),
            data={'liste_adresses' : ADRESSE_TEST + '\nadresse_invalide'})
        nombre_invitations_apres = Invitation.objects.count()
        # on vérifie qu'aucune invitation n'a été ajoutée pour l'adresse invalide
        self.assertEqual(nombre_invitations_apres - nombre_invitations_avant, 1)
        invitation_ajoutee = Invitation.objects.get(courriel=ADRESSE_TEST)
        self.assertEqual(invitation_ajoutee.etablissement.id,
            inscription.get_etablissement().id)
        self.assertRedirects(response, 'inscription/confirmation/#invitation')
        response = self.client.get(url_etape(inscription, 'confirmation'))
        self.assertContains(response, ADRESSE_TEST)

    def test_facturation(self):
        inscription = self.create_inscription(['renseignements-personnels',
                                               'transport-hebergement',])
        total_attendu = infos_montant_par_code('frais_inscription').montant
        self.assertEqual(inscription.get_montant_total(),
                total_attendu)


@mock.patch('ag.inscription.views.inscriptions_terminees', lambda: True)
class FinInscriptionsTestCase(TestCase, InscriptionTestMixin):
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
        inscription = self.create_inscription(['renseignements-personnels'])
        response = self.client.get('/inscription/connexion/' +
                                   inscription.invitation.jeton)
        self.assertRedirects(response, reverse('inscriptions_terminees'))

    def test_inscrit(self):
        inscription = self.create_inscription(['renseignements-personnels'])
        inscription.fermee = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'accueil'))
        self.assertRedirects(response, url_etape(inscription, 'confirmation'))

    def test_pas_d_invitations(self):
        inscription = self.create_inscription(['renseignements-personnels'])
        inscription.fermee = True
        inscription.save()
        response = self.client.get(url_etape(inscription, 'confirmation'))
        self.assertNotContains(response, u'Invitations aux accompagnateurs')
        self.assertNotContains(response, u'Invitez vos accompagnateurs')

    def test_ajout_invitations_bloque(self):
        inscription = self.create_inscription(['renseignements-personnels'])
        inscription.fermee = True
        inscription.save()
        nb_invitations = Invitation.objects.count()
        self.client.post(reverse('ajout_invitations'), data={
            'liste_adresses': 'abc@mail.net'
        })
        self.assertEqual(nb_invitations, Invitation.objects.count())


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
    assert(inscriptions_terminees())
    FakeDate.today = classmethod(
        lambda cls: settings.DATE_FERMETURE_INSCRIPTIONS -
        datetime.timedelta(days=1))
    assert(not inscriptions_terminees())
