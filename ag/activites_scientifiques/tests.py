# -*- encoding: utf-8 -*-
from ag.gestion.models import ActiviteScientifique
from ag.tests import create_fixtures, creer_participant
from django.core.urlresolvers import reverse
from django.test import TestCase

COURRIEL_TEST = u"participant@activite.com"


class LoginTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')
        self.participant = creer_participant('test_activite_scientifique',
                                             courriel=COURRIEL_TEST)

    def test_not_found(self):
        response = self.client.post(reverse('act_sci_login'), data={
            'email': 'existe_pas@neant.org'
        })
        self.assertRedirects(
            response,
            '{0}?adresse_courriel={1}'.format(
                reverse('act_sci_login_not_found'),
                'existe_pas@neant.org')
        )

    def test_not_found_shows_address(self):
        response = self.client.get('{0}?adresse_courriel={1}'.format(
            reverse('act_sci_login_not_found'),
            'existe_pas@neant.org')
        )
        self.assertContains(response, 'existe_pas@neant.org')

    def test_login_get(self):
        response = self.client.get(reverse('act_sci_login'))
        self.assertEqual(response.status_code, 200)

    def test_found(self):
        response = self.client.post(reverse('act_sci_login'), data={
            'email': COURRIEL_TEST
        })
        self.assertEqual(self.client.session['act_sci_participant_id'],
                         str(self.participant.id))
        self.assertRedirects(response, reverse('act_sci_pick'))

    def test_logout(self):
        self.client.post(reverse('act_sci_login'), data={
            'email': COURRIEL_TEST
        })
        response = self.client.post(reverse('act_sci_logout'))
        self.assertRedirects(response, reverse('act_sci_login'))
        self.assertFalse('act_sci_participant_id' in self.client.session)


class PickTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')
        self.participant = creer_participant('test_activite_scientifique',
                                             courriel=COURRIEL_TEST)

    def login(self):
        self.client.post(reverse('act_sci_login'), data={
            'email': COURRIEL_TEST
        })

    def test_not_logged_in(self):
        response = self.client.get(reverse('act_sci_pick'))
        self.assertRedirects(response, reverse('act_sci_login'))

    def test_options(self):
        self.login()
        response = self.client.get(reverse('act_sci_pick'))
        self.assertEqual(response.status_code, 200)
        activites = ActiviteScientifique.objects.all()
        for activite in activites:
            self.assertContains(response, activite.libelle)
        self.assertNotContains(response, u"COMPLET")

    def test_complet(self):
        activite = ActiviteScientifique.objects.get(code="act1")
        for i in range(10):
            creer_participant('participant' + str(i),
                              activite_scientifique=activite)
        self.login()
        response = self.client.get(reverse('act_sci_pick'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"COMPLET")