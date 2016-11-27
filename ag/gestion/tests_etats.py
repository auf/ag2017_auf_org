# -*- encoding: utf-8 -*-
import StringIO
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
            nom=u'DUNORD', prenom=u'Haggar',
            fonction=fonction_repr_univ,
            etablissement_id=cls.etablissement_nord_id)
        cls.membre_sud = creer_participant(
            nom=u'LESUD', prenom=u'Ganoub',
            fonction=fonction_repr_univ,
            etablissement_id=cls.etablissement_id)
        cls.observateur1 = creer_participant(
            nom=u'OFTHESKIES', prenom=u'Watcher',
            fonction=fonction_obs,
            institution=institution_oif,
            region=cls.region)
        cls.observateur2 = creer_participant(
            nom=u'BLEU', prenom=u'Casque',
            fonction=fonction_obs,
            institution=institution_onu,
            region=cls.region)
        cls.observateur3 = creer_participant(
            nom=u'MOON', prenom=u'Ban Ki',
            fonction=fonction_obs,
            institution=institution_onu,
            region=cls.region)
        cls.observateur4_desactive = creer_participant(
            nom=u'BOUTROS GHALI', prenom=u'BOUTROS',
            fonction=fonction_obs,
            institution=institution_onu,
            desactive=True,
            region=cls.region)
        cls.instance_admin1 = creer_participant(
            nom=u'PRESIDENT', prenom=u'Francis',
            fonction=get_fonction_instance_seulement(),
            instance_auf="A",
            region=cls.region)
        cls.instance_admin2 = creer_participant(
            nom=u'SECRETAIRE', prenom=u'Albert',
            fonction=get_fonction_instance_seulement(),
            instance_auf="A",
            region=cls.region)
        cls.instance_scient1 = creer_participant(
            nom=u'REEVES', prenom=u'Hubert',
            type_institution=Participant.INSTANCE_AUF,
            instance_auf="S",
            code_statut='memb_inst',
            region=cls.region)
        cls.personnel_auf1 = creer_participant(
            nom=u"PELLETIER", prenom=u'Marie-Claude',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_statut=u'pers_auf',
            nom_autre_institution=u'Bureau des Amériques',
            region=cls.region
        )
        cls.personnel_auf2 = creer_participant(
            nom=u"BRUNEAU", prenom=u'Victor',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_type_autre_institution=u'pers_auf',
            code_statut=u'pers_auf',
            nom_autre_institution=u'Bureau des Amériques',
            region=cls.region
        )
        cls.participant_autre1 = creer_participant(
            nom=u"JENSEN", prenom=u'Tomas',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_type_autre_institution=u'repr_press',
            code_statut=u'accomp',
            nom_autre_institution=u'Le Devoir',
            region=cls.region
        )
        cls.participant_autre2 = creer_participant(
            nom=u"FABREG", prenom=u'Doriane',
            type_institution=Participant.AUTRE_INSTITUTION,
            code_type_autre_institution=u'repr_press',
            code_statut=u'accomp',
            nom_autre_institution=u'La Presse',
            region=cls.region
        )
        cls.donnees = get_donnees_etat_participants()

    def setUp(self):
        self.client.login(username='john', password='johnpassword')

    def test_donnees_premier_niveau(self):
        donnees = self.donnees
        titres_premier_niveau = [donnee.titre for donnee in donnees]
        self.assertEqual(titres_premier_niveau,
                         [u'Établissements',
                          u'Observateurs',
                          u'Instances',
                          u'Personnel AUF',
                          u'Autre', ])

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
                         (u"OIF, " + self.region.nom,
                          [self.observateur1]))
        self.assertEqual(elements[1],
                         (u"ONU, " + self.region.nom,
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
            (self.participant_autre2.nom_autre_institution + u", "
             + self.region.nom,
             [self.participant_autre2])
        )

    def test_page(self):
        response = self.client.get(reverse('etat_inscrits'))
        self.assertEqual(response.status_code, 200)


def test_recursive_group_by():
    l = [
        ((u'I', u'Italie'), u'Entrées', u'Salades', u'Salade d\'artichauts'),
        ((u'I', u'Italie'), u'Entrées', u'Salades', u'Salade de poivrons'),
        ((u'I', u'Italie'), u'Entrées', u'Salades', u'Salade verte'),
        ((u'I', u'Italie'), u'Plats', u'Pasta', u'Fetuccine Carbonara'),
        ((u'I', u'Italie'), u'Plats', u'Pizza', u'Margherita'),
        ((u'I', u'Italie'), u'Plats', u'Pizza', u'Napolitaine'),
        ((u'L', u'Liban'), u'Entrées', u'Salades', u'Fatouche'),
        ((u'L', u'Liban'), u'Entrées', u'Salades', u'Riz-lentilles'),
        ((u'L', u'Liban'), u'Entrées', u'Salades', u'Tabbouleh'),
        ((u'L', u'Liban'), u'Plats', u'Légumes', u'Chou farci'),
        ((u'L', u'Liban'), u'Plats', u'Légumes', u'Feuilles de vigne'),
        ((u'L', u'Liban'), u'Plats', u'Viande', u'Kebab'),
    ]
    result = recursive_group_by(l,
                                keys=[lambda item: item[0][0],
                                      lambda item: item[1],
                                      lambda item: item[2]],
                                titles=[lambda item: u'Pays:' + item,
                                        lambda item: u'Service:' + item,
                                        lambda item: u'Type:' + item])
    assert(len(result) == 2)
    assert(result[0].titre == u'Pays:I')
    assert(result[1].titre == u'Pays:L')
    assert(len(result[0].elements) == 2)
    assert(len(result[1].elements) == 2)
    assert(result[0].elements[0].titre == u'Service:Entrées')
    assert(result[0].elements[1].titre == u'Service:Plats')
    assert(result[0].elements[0].elements[0].titre == u'Type:Salades')
    assert(result[0].elements[0].elements[0].elements == [l[0], l[1], l[2]])
    assert(result[0].elements[1].elements[0].elements == [l[3]])
    assert(result[0].elements[1].elements[1].elements == [l[4], l[5]])
    assert(result[1].elements[0].elements[0].elements == [l[6], l[7], l[8]])
    assert(result[1].elements[1].elements[0].elements == [l[9], l[10]])
    assert(result[1].elements[1].elements[1].elements == [l[11]])

VILLE_PARIS = u'PARIS'
VILLE_BORDEAUX = u'BORDEAUX'
VILLE_SAO_PAULO = u'SAO PAULO'
DATE_DEPART_ORIGINE = datetime.date(2013, 5, 4)
DATE_ARRIVEE_AG = datetime.date(2013, 5, 5)
DATE_DEPART_AG = datetime.date(2013, 5, 6)
DATE_ARRIVEE_ORIGINE = datetime.date(2013, 5, 7)
DATE_ARRIVEE_ORIGINE2 = datetime.date(2013, 5, 8)
COMPAGNIE = u'AIR BRESIL'
HEURE_DEPART_ORIGINE_1900 = datetime.time(19, 00)
HEURE_DEPART_ORIGINE_2000 = datetime.time(20, 00)
HEURE_ARRIVEE_AG_1200 = datetime.time(12, 00)
HEURE_ARRIVEE_AG_1300 = datetime.time(13, 00)
HEURE_DEPART_AG_1400 = datetime.time(14, 00)
HEURE_DEPART_AG_1500 = datetime.time(15, 00)
HEURE_ARRIVEE_ORIGINE_0800 = datetime.time(8, 00)
HEURE_ARRIVEE_ORIGINE_0900 = datetime.time(9, 00)
NO_VOL_ARRIVEE_AG_1200 = u'AB123'
NO_VOL_ARRIVEE_AG_1300 = u'CD345'
NO_VOL_DEPART_AG_1400 = u'EF789'
NO_VOL_DEPART_AG_1500 = u'GH098'


class EtatsVolsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'test_data.json')
        create_fixtures(cls)
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
        cls.vol_groupe1, cls.vol_groupe2 = vol_groupe1, vol_groupe2
        cls.participant1 = creer_participant(
            'UN', 'a', genre='M', transport_organise_par_auf=True)
        cls.participant1.prise_en_charge_transport = True
        cls.participant1.prise_en_charge_sejour = True
        cls.participant1.vol_groupe = vol_groupe1
        cls.participant1.save()
        cls.participant2 = creer_participant(
            'DEUX', 'b', genre='F', transport_organise_par_auf=True)
        cls.participant2.vol_groupe = vol_groupe2
        cls.participant2.save()
        cls.participant3 = creer_participant(
            'TROIS', 'c', genre='M', transport_organise_par_auf=True)
        cls.participant3.vol_groupe = vol_groupe2
        cls.participant3.save()
        cls.participant4 = creer_participant(
            'QUATRE', 'd', genre='F', transport_organise_par_auf=True)
        cls.participant4.vol_groupe = vol_groupe2
        cls.participant4.save()
        # arrive dans le même avion que vol groupé 1, mais ne fait
        # pas partie de vol groupé 1
        cls.participant5 = creer_participant(
            'CINQ', 'e', genre='M', transport_organise_par_auf=False)
        cls.participant5.set_infos_arrivee(DATE_ARRIVEE_AG,
                                            HEURE_ARRIVEE_AG_1200,
                                            NO_VOL_ARRIVEE_AG_1200,
                                            COMPAGNIE,
                                            VILLE_SAO_PAULO)
        cls.participant6 = creer_participant(
            'SIX', 'f', genre='F', transport_organise_par_auf=True)
        cls.participant6.vol_groupe = vol_groupe2
        cls.participant6.desactive = True
        cls.participant6.save()
        # SEPT a des infos de vol non organise et des infos de vol
        # organise mais son transport est organise.
        cls.participant7 = creer_participant(
            'SEPT', 'g', genre='M', transport_organise_par_auf=True)
        cls.participant7.set_infos_arrivee(DATE_ARRIVEE_AG,
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
            participant=cls.participant7, type_infos=VOL_ORGANISE,
            numero_vol=NO_VOL_ARRIVEE_AG_1300, compagnie=COMPAGNIE)
        Invite.objects.create(participant=cls.participant5,
                              genre='M',
                              nom='INVITE_DU_5',
                              prenom='edouard')

    def setUp(self):
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
                VILLE_SAO_PAULO, ARRIVEE_STR, u"", None, [self.participant5]) +
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
            self.assertIn(p.nom, response.content)

    def test_etat_tous_vols_csv(self):
        response = self.client.get(reverse('etat_vols_csv'))
        self.assertEqual(response.status_code, 200)
        for p in [self.participant1, self.participant2, self.participant3,
                  self.participant4, self.participant5]:
            self.assertIn(p.nom, response.content)


class EtatParticipantsActivitesTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'test_data.json')
        create_fixtures(cls)
        hotel = Hotel.objects.get(code=CODE_HOTEL)
        activite1, activite2 = Activite.objects.all()[:2]
        cls.participant1 = creer_participant('premier', 'alain')
        cls.participant1.genre = 'M'
        cls.participant1.hotel = hotel
        cls.participant1.inscrire_a_activite(activite1, avec_invites=True)
        cls.participant1.inscrire_a_activite(activite2, avec_invites=False)
        cls.participant1.save()
        cls.participant1.invite_set.add(Invite.objects.create(
            genre='F', nom='premier', prenom='invite',
            participant=cls.participant1))
        cls.participant2 = creer_participant('deuxième', 'thérèse')
        cls.participant2.genre = 'F'
        cls.participant2.hotel = hotel
        cls.participant2.inscrire_a_activite(activite2, avec_invites=True)
        cls.participant2.save()
        cls.participant2.invite_set.add(Invite.objects.create(
            genre='F', nom='deux1', prenom='invite',
            participant=cls.participant2))
        cls.participant2.invite_set.add(Invite.objects.create(
            genre='F', nom='deux2', prenom='invite',
            participant=cls.participant2))
        cls.participant3 = creer_participant('desactivée', 'josette')
        cls.participant3.desactive = True
        cls.participant3.genre = 'F'
        cls.participant3.hotel = hotel
        cls.participant3.inscrire_a_activite(activite2, avec_invites=True)
        cls.participant3.save()
        cls.participant4 = creer_participant(u"pas d'hôtel", 'alain')
        cls.participant4.desactive = True
        cls.participant4.genre = 'M'
        cls.participant4.inscrire_a_activite(activite2, avec_invites=True)
        cls.participant4.save()

    def setUp(self):
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
        itdonnees = iter(donnees.items())
        for activite_attendue in Activite.objects.order_by('libelle').all():
            activite, hotels = next(itdonnees)
            self.assertEqual(activite.libelle, activite_attendue.libelle)
            ithotels = iter(hotels.items())
            for hotel in Hotel.objects.order_by('libelle').all():
                hotel_libelle, participants = next(ithotels)
                self.assertEqual(hotel_libelle, hotel.libelle)
                itparticipants = iter(participants.items())
                for participant in Participant.objects.filter(
                        hotel=hotel,
                        participationactivite__activite=activite_attendue)\
                        .order_by('nom', 'prenom'):
                    check_participant(participant, activite_attendue,
                                      itparticipants)
            sans_hotel_libelle, participants = next(ithotels)
            self.assertEqual(sans_hotel_libelle, u"(Aucun hôtel sélectionné)")
            itparticipants = iter(participants.items())
            for participant in Participant.objects.filter(
                hotel=None, participationactivite__activite=activite_attendue
            ).order_by('nom', 'prenom'):
                check_participant(participant, activite_attendue,
                                  itparticipants)

    def test_etat(self):
        response = self.client.get(reverse('etat_activites'))
        self.assertEqual(response.status_code, 200)


@pytest.mark.skip
class VoteTestCase(TestCase):

    def setUp(self):
        self.client.login(username='john', password='johnpassword')

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'test_data.json')
        create_fixtures(cls)
        cls.participant = creer_participant()
        region_MO = Region.objects.create(code=u'MO',
                                          nom=u'Moyen-Orient')
        region_EO = Region.objects.create(code=u'EO',
                                          nom=u"Europe de l'Ouest")
        pays_fr = Pays.objects.create(
            nom=u"France", code=u"FR", sud=False)
        pays_de = Pays.objects.create(
            nom=u"Allemagne", code=u"DE", sud=False)
        pays_eg = Pays.objects.create(
            nom=u"Égypte", code=u"EG", sud=True)
        etablissement_MO = Etablissement.objects.create(
            nom=u'etab_mo', pays=pays_eg, region=region_MO, statut=u'A',
            qualite=u'ESR', membre=True)
        etablissement_FR = Etablissement.objects.create(
            nom=u'etab_fr', pays=pays_fr, region=region_EO, statut=u'T',
            qualite=u'ESR', membre=True)
        etablissement_DE = Etablissement.objects.create(
            nom=u'etab_de', pays=pays_de, region=region_EO, statut=u'T',
            qualite=u'ESR', membre=True)
        etablissement_DOM_TOM = Etablissement.objects.create(
            id=consts.EXCEPTIONS_DOM_TOM[0],
            nom=u'etab_dom_tom', pays=pays_fr, region=region_MO, statut=u'T',
            qualite=u'ESR', membre=True)
        fonctions = dict((fonction.code, fonction)
                         for fonction in Fonction.objects.all())

        def creer_participant_vote(
                etablissement, pour_mandate=True,
                code_fonction=consts.FONCTION_REPR_UNIVERSITAIRE):
            invitation = Invitation.objects.create(
                pour_mandate=pour_mandate,
                etablissement=etablissement)
            inscription = Inscription.objects.create(invitation=invitation)
            participant = creer_participant()
            participant.etablissement = etablissement
            participant.inscription = inscription
            participant.fonction = fonctions[code_fonction]
            participant.fonction = get_fonction_repr_universitaire()
            participant.save()
            return participant

        cls.participant_MO = creer_participant_vote(etablissement_MO)
        cls.participant_FR = creer_participant_vote(etablissement_FR)
        cls.participant_FR_sans_vote = creer_participant_vote(
            etablissement_FR, pour_mandate=False,
            code_fonction=consts.FONCTION_ACCOMP_UNIVERSITAIRE)
        cls.participant_DE = creer_participant_vote(etablissement_DE)
        cls.participant_DOM_TOM = creer_participant_vote(etablissement_DOM_TOM)
        participant_sans_invitation = Participant()
        participant_sans_invitation.nom = u"Sans-invit"
        participant_sans_invitation.prenom = u"Annie"
        participant_sans_invitation.fonction = get_fonction_repr_universitaire()
        participant_sans_invitation.etablissement = etablissement_DE
        participant_sans_invitation.save()
        participant_desactive = creer_participant_vote(etablissement_DE)
        participant_desactive.desactive = True
        participant_desactive.save()
        cls.participant_DE_sans_invitation = participant_sans_invitation

    def tearDown(self):
        self.client.logout()

    def get_region_vote_participant(self, participant):
        p = Participant.objects.avec_region_vote()
        p = p.get(id=participant.id)
        return p.region_vote

    def test_MO(self):
        region = self.get_region_vote_participant(self.participant_MO)
        self.assertEquals(region, consts.REG_MOYEN_ORIENT)

    def test_filtre_MO(self):
        p = Participant.objects.filter_region_vote(consts.REG_MOYEN_ORIENT)
        self.assertEqual(list(p), [self.participant_MO])

    def test_EO(self):
        region = self.get_region_vote_participant(self.participant_DE)
        self.assertEquals(region, consts.REG_EUROPE_OUEST)

    def test_filtre_EO(self):
        p = list(Participant.objects.filter_region_vote(
            consts.REG_EUROPE_OUEST))
        self.assertTrue(self.participant_DOM_TOM in p)
        self.assertTrue(self.participant_DE_sans_invitation in p)
        self.assertEqual(len(p), 4)
        self.assertTrue(self.participant_DE in p)
        self.assertTrue(self.participant_FR in p)

    def test_sans_droit_de_vote(self):
        region = self.get_region_vote_participant(
            self.participant_FR_sans_vote)
        self.assertEquals(region, None)

    def test_DOM_TOM(self):
        region = self.get_region_vote_participant(
            self.participant_DOM_TOM)
        self.assertEquals(region, consts.REG_EUROPE_OUEST)

    def test_nombre_votants_fr(self):
        donnees_regions, totaux = get_nombre_votants_par_region()
        donnees_fr = filter(
            lambda x: x[0] == u"dont France", donnees_regions
        )[0]
        self.assertEquals(donnees_fr[1:], (2, 0, 2))

    def test_nombre_votants_mo(self):
        donnees_regions, totaux = get_nombre_votants_par_region()
        donnees_mo = filter(
            lambda x: x[0] == u"Moyen-Orient", donnees_regions
        )[0]
        self.assertEquals(donnees_mo[1:], (0, 1, 1))

    def test_nombre_votants_eo(self):
        donnees_regions, totaux = get_nombre_votants_par_region()
        donnees_eo = filter(
            lambda x: x[0] == u"Europe de l'Ouest", donnees_regions
        )[0]
        self.assertEquals(donnees_eo[1:], (4, 0, 4))

    def test_nombre_votants_total(self):
        donnees_regions, totaux = get_nombre_votants_par_region()
        # la France ne compte pas deux fois !
        self.assertEquals(totaux, (4, 1, 5))

    def test_csv(self):
        response = self.client.get(reverse('votants_csv'))
        si = StringIO.StringIO(response.content)
        csv_reader = csv.reader(si, delimiter=',', quotechar='"')
        rows = [line for line in csv_reader]
        # participants + entête
        self.assertEqual(len(rows), 6)

    def test_etat_votants(self):
        response = self.client.get(reverse('etat_votants'))
        self.assertEqual(response.content.count('<tr'), 6)


class ExportParticipantsTestCase(TestCase):
    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')

    def tearDown(self):
        self.client.logout()

    def test_export(self):
        response = self.client.get(reverse('export_donnees_csv'))
        self.assertEqual(response.status_code, 200)
