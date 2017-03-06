# -*- encoding: utf-8 -*-

from django.db.models import IntegerField

from ag.core.models import TableReferenceOrdonnee


class Election(TableReferenceOrdonnee):
    class Meta:
        ordering = ['ordre']

    nb_sieges_global = IntegerField(u"Global", blank=True, null=True)
    nb_sieges_afrique = IntegerField(u"Afrique", blank=True, null=True)
    nb_sieges_ameriques = IntegerField(u"Amériques", blank=True, null=True)
    nb_sieges_asie_pacifique = IntegerField(u"Asie-Pacifique",
                                            blank=True, null=True)
    nb_sieges_europe_ouest = IntegerField(u"Europe de l'ouest",
                                          blank=True, null=True)
    nb_sieges_europe_est = IntegerField(u"Europe centrale et orientale",
                                        blank=True, null=True)
    nb_sieges_maghreb = IntegerField(u"Maghreb", blank=True, null=True)
    nb_sieges_moyen_orient = IntegerField(u"Moyen-Orient", blank=True,
                                          null=True)

    def __unicode__(self):
        return self.code
