# encoding: utf-8

from django.db import models
from django.db.models import Model, CharField, IntegerField


class EtablissementDelinquant(models.Model):
    """
    Extension des données de référence sur les établissements.
    """
    id = models.IntegerField(db_column='id', primary_key=True)


class TableReference(Model):
    class Meta:
        abstract = True
    code = CharField(max_length=16, blank=True)
    libelle = CharField(u"Libellé", max_length=256)

    def __unicode__(self):
        return self.libelle


class TableReferenceOrdonnee(TableReference):
    ordre = IntegerField()

    class Meta:
        abstract = True
        ordering = ['ordre', 'libelle']