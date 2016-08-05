# -*- encoding: utf-8 -*-

from django.db import models


class Pays(models.Model):
    code = models.CharField(max_length=2, unique=True)
    nom = models.CharField(max_length=255)
    sud = models.BooleanField()

    def get_sud_display(self):
        return u"sud" if self.sud else u"nord"


class Region(models.Model):
    code = models.CharField(max_length=255, unique=True)
    nom = models.CharField(max_length=255)


class Etablissement(models.Model):
    STATUT_CHOICES = (
        ('T', 'Titulaire'),
        ('A', 'Associé'),
        ('C', 'Candidat'),
    )
    QUALITE_CHOICES = (
        ('ESR', "Établissement d'enseignement supérieur et de recherche"),
        ('CIR', "Centre ou institution de recherche"),
        ('RES', "Réseau"),
    )

    nom = models.CharField(max_length=255)
    pays = models.ForeignKey(Pays)
    region = models.ForeignKey(Region, blank=True, null=True,
                               verbose_name='région')
    adresse = models.CharField(max_length=255, blank=True)
    code_postal = models.CharField(u'code postal', max_length=20, blank=True)
    ville = models.CharField(max_length=255, blank=True)
    telephone = models.CharField(u'téléphone', max_length=255, blank=True)
    fax = models.CharField(max_length=255, blank=True)

    responsable_courriel = models.EmailField(u'courriel', blank=True)

    statut = models.CharField(
        max_length=1, choices=STATUT_CHOICES, blank=True, null=True)

    qualite = models.CharField(
        u'qualité', max_length=3, choices=QUALITE_CHOICES, blank=True,
        null=True
    )
    membre = models.BooleanField(default=False)