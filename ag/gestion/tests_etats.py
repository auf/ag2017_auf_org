# -*- encoding: utf-8 -*-
import io
import csv
import pytest
from django.core.management import call_command

from ag.core.test_utils import TypeInstitutionFactory, FonctionFactory, \
    InstitutionFactory
from ag.gestion.donnees_etats import *
from ag.gestion.models import *
from ag.gestion.models import get_fonction_repr_universitaire, \
    get_fonction_instance_seulement
from ag.gestion.tests import CODE_HOTEL
from ag.inscription.models import Invitation, Inscription
from ag.tests import create_fixtures, creer_participant
from ag.reference.models import Pays, Etablissement, Region
from django.core.urlresolvers import reverse
from django.test import TestCase


# noinspection PyUnresolvedReferences
@pytest.mark.skip()
class EtatParticipantsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'test_data.json')
        create_fixtures(cls)
        type_institution_obs = TypeInstitutionFactory()
        fonction_obs = FonctionFactory(type_institution=type_institution_obs)
        fonction_repr_univ = get_fonction_repr_universitaire()
        institution_oif = InstitutionFactory(
            region=cls.region,
            type_institution=type_institution_obs)
        institution_onu = InstitutionFactory(
            region=cls.region,
            type_institution=type_institution_obs)
        cls.membre_nord = creer_participant(
            nom='DUNORD', prenom='Haggar',
            fonction=fonction_repr_univ,
            etablissement_id=cls.etablissement_nord_id)
        cls.membre_sud = creer_participant(
            nom='LESUD', prenom='Ganoub',
            fonction=fonction_repr_univ,
            etablissement_id=cls.etablissement_id)
        cls.observateur1 = creer_participant(
            nom='OFTHESKIES', prenom='Watcher',
            fonction=fonction_obs,
            institution=institution_oif,
            region=cls.region)
        cls.observateur2 = creer_participant(
            nom='BLEU', prenom='Casque',
            fonction=fonction_obs,
            institution=institution_onu,
            region=cls.region)
        cls.observateur3 = creer_participant(
            nom='MOON', prenom='Ban Ki',
            fonction=fonction_obs,
            institution=institution_onu,
            region=cls.region)
        cls.observateur4_desactive = creer_participant(
            nom='BOUTROS GHALI', prenom='BOUTROS',
            fonction=fonction_obs,
            institution=institution_onu,
            desactive=True,
            region=cls.region)
        fonction_instance_seulement = get_fonction_instance_seulement()
        cls.instance_admin1 = creer_participant(
            nom='PRESIDENT', prenom='Francis',
            fonction=fonction_instance_seulement,
            instance_auf="A",
            region=cls.region)
        cls.instance_admin2 = creer_participant(
            nom='SECRETAIRE', prenom='Albert',
            fonction=fonction_instance_seulement,
            instance_auf="A",
            region=cls.region)
        cls.instance_scient1 = creer_participant(
            nom='REEVES', prenom='Hubert',
            instance_auf="S",
            fonction=fonction_instance_seulement)
        cls.personnel_auf1 = creer_participant(
            nom="PELLETIER", prenom='Marie-Claude',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_statut='pers_auf',
            nom_autre_institution='Bureau des Amériques',
            region=cls.region
        )
        cls.personnel_auf2 = creer_participant(
            nom="BRUNEAU", prenom='Victor',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_type_autre_institution='pers_auf',
            code_statut='pers_auf',
            nom_autre_institution='Bureau des Amériques',
            region=cls.region
        )
        cls.participant_autre1 = creer_participant(
            nom="JENSEN", prenom='Tomas',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_type_autre_institution='repr_press',
            code_statut='accomp',
            nom_autre_institution='Le Devoir',
            region=cls.region
        )
        cls.participant_autre2 = creer_participant(
            nom="FABREG", prenom='Doriane',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_type_autre_institution='repr_press',
            code_statut='accomp',
            nom_autre_institution='La Presse',
            region=cls.region
        )
        cls.donnees = get_donnees_etat_participants()

    def setUp(self):
        self.client.login(username='john', password='johnpassword')

    def test_donnees_premier_niveau(self):
        donnees = self.donnees
        titres_premier_niveau = [donnee.titre for donnee in donnees]
        self.assertEqual(titres_premier_niveau,
                         ['Établissements',
                          'Observateurs',
                          'Instances',
                          'Personnel AUF',
                          'Autre', ])

    def test_donnees_etablissement_premier_niveau_pays_tries(self):
        elements = self.donnees[0].elements
        self.assertEqual(len(elements), 2)
        noms_pays = [pays.nom for pays in Pays.objects.order_by('nom').all()]
        titres = [e.titre for e in elements]
        assert titres == noms_pays

    def test_donnees_etablissement_etablissement_statut(self):
        elements = self.donnees[0].elements
        elements_sud = [e for e in elements if e.titre == self.pays_sud.nom]
        elements_pays_sud = elements_sud[0].elements
        etablissement_sud = Etablissement.objects.get(id=self.etablissement_id)
        self.assertEqual(elements_pays_sud[0].titre, etablissement_sud.nom)
        self.fail()
        # statut_repr_tit = StatutParticipant.objects.get(code='repr_tit')
        # self.assertEqual(elements_pays_sud[0].elements,
        #                  [(statut_repr_tit.libelle, [self.membre_sud])])

    def test_donnees_observateurs(self):
        elements = self.donnees[1].elements
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0],
                         ("OIF, " + self.region.nom,
                          [self.observateur1]))
        self.assertEqual(elements[1],
                         ("ONU, " + self.region.nom,
                          [self.observateur2, self.observateur3]))

    def test_donnees_instances(self):
        elements = self.donnees[2].elements
        instances_noms = dict(Participant.INSTANCES_AUF)
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0],
                         (instances_noms['A'],
                          [self.instance_admin1, self.instance_admin2]))
        self.assertEqual(elements[1],
                         (instances_noms['S'],
                          [self.instance_scient1]))

    def test_donnees_personnel_auf(self):
        elements = self.donnees[3].elements
        self.assertEqual(len(elements), 1)
        elements_bureau_am = elements[0].elements
        self.assertEqual(
            elements_bureau_am,
            [(self.region.nom, [self.personnel_auf2, self.personnel_auf1])]
        )

    def test_donnees_autres(self):
        elements = self.donnees[4].elements
        self.assertEqual(len(elements), 2)
        self.assertEqual(
            elements[0],
            (self.participant_autre2.nom_autre_institution + ", "
             + self.region.nom,
             [self.participant_autre2])
        )

    def test_page(self):
        response = self.client.get(reverse('etat_inscrits'))
        self.assertEqual(response.status_code, 200)


def test_recursive_group_by():
    l = [
        (('I', 'Italie'), 'Entrées', 'Salades', 'Salade d\'artichauts'),
        (('I', 'Italie'), 'Entrées', 'Salades', 'Salade de poivrons'),
        (('I', 'Italie'), 'Entrées', 'Salades', 'Salade verte'),
        (('I', 'Italie'), 'Plats', 'Pasta', 'Fetuccine Carbonara'),
        (('I', 'Italie'), 'Plats', 'Pizza', 'Margherita'),
        (('I', 'Italie'), 'Plats', 'Pizza', 'Napolitaine'),
        (('L', 'Liban'), 'Entrées', 'Salades', 'Fatouche'),
        (('L', 'Liban'), 'Entrées', 'Salades', 'Riz-lentilles'),
        (('L', 'Liban'), 'Entrées', 'Salades', 'Tabbouleh'),
        (('L', 'Liban'), 'Plats', 'Légumes', 'Chou farci'),
        (('L', 'Liban'), 'Plats', 'Légumes', 'Feuilles de vigne'),
        (('L', 'Liban'), 'Plats', 'Viande', 'Kebab'),
    ]
    result = recursive_group_by(l,
                                keys=[lambda item: item[0][0],
                                      lambda item: item[1],
                                      lambda item: item[2]],
                                titles=[lambda item: 'Pays:' + item,
                                        lambda item: 'Service:' + item,
                                        lambda item: 'Type:' + item])
    assert(len(result) == 2)
    assert(result[0].titre == 'Pays:I')
    assert(result[1].titre == 'Pays:L')
    assert(len(result[0].elements) == 2)
    assert(len(result[1].elements) == 2)
    assert(result[0].elements[0].titre == 'Service:Entrées')
    assert(result[0].elements[1].titre == 'Service:Plats')
    assert(result[0].elements[0].elements[0].titre == 'Type:Salades')
    assert(result[0].elements[0].elements[0].elements == [l[0], l[1], l[2]])
    assert(result[0].elements[1].elements[0].elements == [l[3]])
    assert(result[0].elements[1].elements[1].elements == [l[4], l[5]])
    assert(result[1].elements[0].elements[0].elements == [l[6], l[7], l[8]])
    assert(result[1].elements[1].elements[0].elements == [l[9], l[10]])
    assert(result[1].elements[1].elements[1].elements == [l[11]])

VILLE_PARIS = 'PARIS'
VILLE_BORDEAUX = 'BORDEAUX'
VILLE_SAO_PAULO = 'SAO PAULO'
DATE_DEPART_ORIGINE = datetime.date(2013, 5, 4)
DATE_ARRIVEE_AG = datetime.date(2013, 5, 5)
DATE_DEPART_AG = datetime.date(2013, 5, 6)
DATE_ARRIVEE_ORIGINE = datetime.date(2013, 5, 7)
DATE_ARRIVEE_ORIGINE2 = datetime.date(2013, 5, 8)
COMPAGNIE = 'AIR BRESIL'
HEURE_DEPART_ORIGINE_1900 = datetime.time(19, 00)
HEURE_DEPART_ORIGINE_2000 = datetime.time(20, 00)
HEURE_ARRIVEE_AG_1200 = datetime.time(12, 00)
HEURE_ARRIVEE_AG_1300 = datetime.time(13, 00)
HEURE_DEPART_AG_1400 = datetime.time(14, 00)
HEURE_DEPART_AG_1500 = datetime.time(15, 00)
HEURE_ARRIVEE_ORIGINE_0800 = datetime.time(8, 00)
HEURE_ARRIVEE_ORIGINE_0900 = datetime.time(9, 00)
NO_VOL_ARRIVEE_AG_1200 = 'AB123'
NO_VOL_ARRIVEE_AG_1300 = 'CD345'
NO_VOL_DEPART_AG_1400 = 'EF789'
NO_VOL_DEPART_AG_1500 = 'GH098'


class EtatsVolsTestCase(TestCase):

    def setUp(self):
        call_command('loaddata', 'test_data.json')
        create_fixtures(self)
        vol_groupe1 = VolGroupe.objects.create(nom='volgroupe1')
        InfosVol.objects.create(
            ville_depart=VILLE_PARIS, date_depart=DATE_DEPART_ORIGINE,
            heure_depart=HEURE_DEPART_ORIGINE_1900, 
            ville_arrivee=VILLE_SAO_PAULO,
            date_arrivee=DATE_ARRIVEE_AG, heure_arrivee=HEURE_ARRIVEE_AG_1200,
            numero_vol=NO_VOL_ARRIVEE_AG_1200, compagnie=COMPAGNIE,
            vol_groupe=vol_groupe1, type_infos=consts.VOL_GROUPE)
        InfosVol.objects.create(
            ville_depart=VILLE_SAO_PAULO, date_depart=DATE_DEPART_AG,
            heure_depart=HEURE_DEPART_AG_1400, ville_arrivee=VILLE_PARIS,
            date_arrivee=DATE_ARRIVEE_ORIGINE,
            heure_arrivee=HEURE_ARRIVEE_ORIGINE_0800,
            numero_vol=NO_VOL_DEPART_AG_1400, compagnie=COMPAGNIE,
            vol_groupe=vol_groupe1, type_infos=consts.VOL_GROUPE)
        vol_groupe2 = VolGroupe.objects.create(nom='volgroupe2')
        InfosVol.objects.create(
            ville_depart=VILLE_BORDEAUX, date_depart=DATE_DEPART_ORIGINE,
            heure_depart=HEURE_DEPART_ORIGINE_2000,
            ville_arrivee=VILLE_SAO_PAULO,
            date_arrivee=DATE_ARRIVEE_AG, 
            heure_arrivee=HEURE_ARRIVEE_AG_1300,
            vol_groupe=vol_groupe2, type_infos=consts.VOL_GROUPE,
            numero_vol=NO_VOL_ARRIVEE_AG_1300, compagnie=COMPAGNIE,)
        InfosVol.objects.create(
            ville_depart=VILLE_SAO_PAULO, date_depart=DATE_ARRIVEE_AG,
            heure_depart=HEURE_DEPART_AG_1500, ville_arrivee=VILLE_BORDEAUX,
            numero_vol=NO_VOL_DEPART_AG_1500,
            date_arrivee=DATE_ARRIVEE_ORIGINE2,
            heure_arrivee=HEURE_ARRIVEE_ORIGINE_0900,
            vol_groupe=vol_groupe2,  compagnie=COMPAGNIE,
            type_infos=consts.VOL_GROUPE)
        self.vol_groupe1, self.vol_groupe2 = vol_groupe1, vol_groupe2
        self.participant1 = creer_participant(
            'UN', 'a', genre='M', transport_organise_par_auf=True)
        self.participant1.prise_en_charge_transport = True
        self.participant1.prise_en_charge_sejour = True
        self.participant1.vol_groupe = vol_groupe1
        self.participant1.save()
        self.participant2 = creer_participant(
            'DEUX', 'b', genre='F', transport_organise_par_auf=True)
        self.participant2.vol_groupe = vol_groupe2
        self.participant2.save()
        self.participant3 = creer_participant(
            'TROIS', 'c', genre='M', transport_organise_par_auf=True)
        self.participant3.vol_groupe = vol_groupe2
        self.participant3.save()
        self.participant4 = creer_participant(
            'QUATRE', 'd', genre='F', transport_organise_par_auf=True)
        self.participant4.vol_groupe = vol_groupe2
        self.participant4.save()
        # arrive dans le même avion que vol groupé 1, mais ne fait
        # pas partie de vol groupé 1
        self.participant5 = creer_participant(
            'CINQ', 'e', genre='M', transport_organise_par_auf=False)
        self.participant5.set_infos_arrivee(DATE_ARRIVEE_AG,
                                            HEURE_ARRIVEE_AG_1200,
                                            NO_VOL_ARRIVEE_AG_1200,
                                            COMPAGNIE,
                                            VILLE_SAO_PAULO)
        self.participant6 = creer_participant(
            'SIX', 'f', genre='F', transport_organise_par_auf=True)
        self.participant6.vol_groupe = vol_groupe2
        self.participant6.desactive = True
        self.participant6.save()
        # SEPT a des infos de vol non organise et des infos de vol
        # organise mais son transport est organise.
        self.participant7 = creer_participant(
            'SEPT', 'g', genre='M', transport_organise_par_auf=True)
        self.participant7.set_infos_arrivee(DATE_ARRIVEE_AG,
                                            HEURE_ARRIVEE_AG_1200,
                                            NO_VOL_ARRIVEE_AG_1200,
                                            COMPAGNIE,
                                            VILLE_SAO_PAULO)
        InfosVol.objects.create(
            ville_depart=VILLE_BORDEAUX, date_depart=DATE_DEPART_ORIGINE,
            heure_depart=HEURE_DEPART_ORIGINE_2000,
            ville_arrivee=VILLE_SAO_PAULO,
            date_arrivee=DATE_ARRIVEE_AG,
            heure_arrivee=HEURE_ARRIVEE_AG_1300,
            participant=self.participant7, type_infos=VOL_ORGANISE,
            numero_vol=NO_VOL_ARRIVEE_AG_1300, compagnie=COMPAGNIE)
        Invite.objects.create(participant=self.participant5,
                              genre='M',
                              nom='INVITE_DU_5',
                              prenom='edouard')
        self.client.login(username='john', password='johnpassword')

    def tearDown(self):
        self.client.logout()

    def test_get_dates_arrivees(self):
        dates = get_dates_arrivees()
        self.assertEqual(dates, [DATE_ARRIVEE_AG,
                                 DATE_ARRIVEE_ORIGINE,
                                 DATE_ARRIVEE_ORIGINE2])

    def test_get_dates_departs(self):
        dates = get_dates_departs()
        self.assertEqual(dates, [DATE_DEPART_ORIGINE,
                                 DATE_ARRIVEE_AG,
                                 DATE_DEPART_AG])

    def donnees_tous_vols_par_jour(self, jour):
        donnees = get_donnees_tous_vols()
        donnees = [donnee for donnee in donnees if donnee.date1 == jour]
        return donnees

    def test_donnees_tous_vols_depart_origine(self):
        donnees = self.donnees_tous_vols_par_jour(DATE_DEPART_ORIGINE)
        self.assertEqual(
            donnees,
            self.gen_donnees_tous_vols(
                DATE_DEPART_ORIGINE, HEURE_DEPART_ORIGINE_1900,
                NO_VOL_ARRIVEE_AG_1200, VILLE_PARIS, DEPART_STR,
                VILLE_SAO_PAULO, DATE_ARRIVEE_AG, [self.participant1]) +
            self.gen_donnees_tous_vols(
                DATE_DEPART_ORIGINE, HEURE_DEPART_ORIGINE_2000,
                NO_VOL_ARRIVEE_AG_1300, VILLE_BORDEAUX, DEPART_STR,
                VILLE_SAO_PAULO, DATE_ARRIVEE_AG,
                [self.participant2, self.participant3, self.participant4,
                 self.participant7]
            ))

    def gen_donnees_tous_vols(self, date1, heure1, numero_vol, ville1,
                              dep_arr, ville2, date2, participants):
        participants.sort(key=lambda p: p.get_nom_prenom_sans_accents())
        return [LigneVol(
            date1=date1, heure1=heure1, no_vol=numero_vol, ville1=ville1,
            dep_arr=dep_arr,
            vers_de=VERS_STR if dep_arr == DEPART_STR else DE_STR,
            ville2=ville2, date2=date2, genre=p.genre, nom=p.nom,
            prenom=p.prenom, nom_normalise=strip_accents(p.nom),
            prenom_normalise=strip_accents(p.prenom), participant_id=p.id,
            vol_groupe_nom=p.vol_groupe.nom if p.vol_groupe else None,
            vol_groupe_id=p.vol_groupe.id if p.vol_groupe else None,
            prise_en_charge_sejour=p.prise_en_charge_sejour,
            prise_en_charge_transport=p.prise_en_charge_transport,
            compagnie=COMPAGNIE
        ) for p in participants]

    def test_donnees_tous_vols_arrivee_ag(self):
        donnees = self.donnees_tous_vols_par_jour(DATE_ARRIVEE_AG)
        self.assertEqual(
            donnees,
            self.gen_donnees_tous_vols(
                DATE_ARRIVEE_AG, HEURE_ARRIVEE_AG_1200, NO_VOL_ARRIVEE_AG_1200,
                VILLE_SAO_PAULO, ARRIVEE_STR, "", None, [self.participant5]) +
            self.gen_donnees_tous_vols(
                DATE_ARRIVEE_AG, HEURE_ARRIVEE_AG_1200, NO_VOL_ARRIVEE_AG_1200,
                VILLE_SAO_PAULO, ARRIVEE_STR, VILLE_PARIS, DATE_DEPART_ORIGINE,
                [self.participant1]) +
            self.gen_donnees_tous_vols(
                DATE_ARRIVEE_AG, HEURE_ARRIVEE_AG_1300,
                NO_VOL_ARRIVEE_AG_1300, VILLE_SAO_PAULO, ARRIVEE_STR,
                VILLE_BORDEAUX, DATE_DEPART_ORIGINE,
                [self.participant2, self.participant7, self.participant3,
                 self.participant4]) +
            self.gen_donnees_tous_vols(
                DATE_ARRIVEE_AG, HEURE_DEPART_AG_1500,
                NO_VOL_DEPART_AG_1500, VILLE_SAO_PAULO, DEPART_STR,
                VILLE_BORDEAUX, DATE_ARRIVEE_ORIGINE2,
                [self.participant2, self.participant3, self.participant4]))

    def test_etat_tous_vols(self):
        response = self.client.get(reverse('etat_vols'))
        self.assertEqual(response.status_code, 200)
        for p in [self.participant1, self.participant2, self.participant3,
                  self.participant4, self.participant5]:
            self.assertIn(p.nom, response.content.decode("utf-8"))

    def test_etat_tous_vols_csv(self):
        response = self.client.get(reverse('etat_vols_csv'))
        self.assertEqual(response.status_code, 200)
        for p in [self.participant1, self.participant2, self.participant3,
                  self.participant4, self.participant5]:
            self.assertIn(p.nom, response.content.decode("utf-8"))


class EtatParticipantsActivitesTestCase(TestCase):

    def setUp(self):
        call_command('loaddata', 'test_data.json')
        create_fixtures(self)
        hotel = Hotel.objects.get(code=CODE_HOTEL)
        activite1, activite2 = Activite.objects.all()[:2]
        self.participant1 = creer_participant('premier', 'alain')
        self.participant1.genre = 'M'
        self.participant1.hotel = hotel
        self.participant1.inscrire_a_activite(activite1, avec_invites=True)
        self.participant1.inscrire_a_activite(activite2, avec_invites=False)
        self.participant1.save()
        self.participant1.invite_set.add(Invite.objects.create(
            genre='F', nom='premier', prenom='invite',
            participant=self.participant1))
        self.participant2 = creer_participant('deuxième', 'thérèse')
        self.participant2.genre = 'F'
        self.participant2.hotel = hotel
        self.participant2.inscrire_a_activite(activite2, avec_invites=True)
        self.participant2.save()
        self.participant2.invite_set.add(Invite.objects.create(
            genre='F', nom='deux1', prenom='invite',
            participant=self.participant2))
        self.participant2.invite_set.add(Invite.objects.create(
            genre='F', nom='deux2', prenom='invite',
            participant=self.participant2))
        self.participant3 = creer_participant('desactivée', 'josette')
        self.participant3.desactive = True
        self.participant3.genre = 'F'
        self.participant3.hotel = hotel
        self.participant3.inscrire_a_activite(activite2, avec_invites=True)
        self.participant3.save()
        self.participant4 = creer_participant("pas d'hôtel", 'alain')
        self.participant4.desactive = True
        self.participant4.genre = 'M'
        self.participant4.inscrire_a_activite(activite2, avec_invites=True)
        self.participant4.save()
        self.client.login(username='john', password='johnpassword')

    def tearDown(self):
        self.client.logout()

    def test_donnees(self):
        def check_invites(invites, participation_activite):
            if participation_activite.avec_invites:
                participant = participation_activite.participant
                self.assertEqual(
                    invites,
                    list(Invite.objects.filter(participant=participant)
                    .order_by('nom', 'prenom')))
            else:
                self.assertFalse(invites)

        def check_participant(attendu, activite, iter_participant):
                if not attendu.desactive:
                    participant, invites = next(iter_participant)
                    self.assertEqual(attendu, participant)
                    check_invites(
                        invites,
                        attendu.get_participation_activite(activite))

        donnees = get_donnees_participants_activites()
        itdonnees = iter(list(donnees.items()))
        for activite_attendue in Activite.objects.order_by('libelle').all():
            activite, hotels = next(itdonnees)
            self.assertEqual(activite.libelle, activite_attendue.libelle)
            ithotels = iter(list(hotels.items()))
            for hotel in Hotel.objects.order_by('libelle').all():
                hotel_libelle, participants = next(ithotels)
                self.assertEqual(hotel_libelle, hotel.libelle)
                itparticipants = iter(list(participants.items()))
                for participant in Participant.objects.filter(
                        hotel=hotel,
                        participationactivite__activite=activite_attendue)\
                        .order_by('nom', 'prenom'):
                    check_participant(participant, activite_attendue,
                                      itparticipants)
            sans_hotel_libelle, participants = next(ithotels)
            self.assertEqual(sans_hotel_libelle, "(Aucun hôtel sélectionné)")
            itparticipants = iter(list(participants.items()))
            for participant in Participant.objects.filter(
                hotel=None, participationactivite__activite=activite_attendue
            ).order_by('nom', 'prenom'):
                check_participant(participant, activite_attendue,
                                  itparticipants)

    def test_etat(self):
        response = self.client.get(reverse('etat_activites'))
        self.assertEqual(response.status_code, 200)


class ExportParticipantsTestCase(TestCase):
    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')

    def tearDown(self):
        self.client.logout()

    def test_export(self):
        response = self.client.get(reverse('export_donnees_csv'))
        self.assertEqual(response.status_code, 200)
