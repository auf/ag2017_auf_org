# -*- encoding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import TabularInline
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.formats import date_format

from ag.gestion.forms import ValidationInscriptionForm
from ag.gestion.models import Hotel, Chambre, PointDeSuivi,\
    TypeInstitutionSupplementaire, Activite, InscriptionWeb, TypeFrais, \
    AGRole, TYPE_CHAMBRE_CHOICES, Invitation, ActiviteScientifique
from ag.inscription.models import Inscription, Forfait


class RoleInline(admin.TabularInline):
    model = AGRole


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
    inlines = (RoleInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


class ChambreInline(TabularInline):
    model = Chambre
    extra = 2
    max_num = len(TYPE_CHAMBRE_CHOICES)


class HotelAdmin(ModelAdmin):
    inlines = [ChambreInline]


class InscriptionAdmin(ModelAdmin):
    form = ValidationInscriptionForm
    fieldsets = (
        (u"Participant", {'fields': (
            'genre', 'nom', 'prenom', 'nationalite', 'date_naissance',
            'poste', 'courriel', 'adresse', 'ville',  'pays', 'code_postal',
            'telephone', 'telecopieur',
        )}),
        (u"Invité", {'fields': (
            'accompagnateur', 'accompagnateur_genre', 'accompagnateur_nom',
            'accompagnateur_prenom',
        )}),
        (u"Transport et hébergement", {'fields': (
            'prise_en_charge_hebergement', 'facturer_supplement_chambre_double',
            'date_arrivee_hotel', 'date_depart_hotel',
            'prise_en_charge_transport', 'arrivee_date', 'arrivee_heure',
            'arrivee_vol', 'depart_de', 'depart_date',
            'depart_heure', 'depart_vol',
        )}),
        (u"Programmation", {'fields': (
            'programmation_soiree_9_mai',
            'programmation_soiree_10_mai',
            'programmation_gala', 
            'programmation_soiree_12_mai'
        )}),
        (u"Forfaits supplémentaires pour accompagnateurs personnels", {'fields': (
            'programmation_soiree_9_mai_invite',
            'programmation_soiree_10_mai_invite',
            'programmation_gala_invite',
            'forfait_invite_dejeuners', 'forfait_invite_transfert'
        )}),
        (u"Paiement par Paypal", {'fields': ('paiement_paypal_total_str', )}),
        (u"Validation", {'fields': (
            'fermee', 'date_fermeture', 'statut',
            'accepter_hebergement',
            'accepter_transport', 'inscription_validee',
        )}),
    )
    list_filter = ('fermee', 'invitation__etablissement__region')
    search_fields = ['nom', 'invitation__etablissement__nom']
    list_display = (
        'get_nom_prenom', 'get_nom_etablissement', 'get_date_fermeture',
        'get_nom_region', 'numero',
    )
    list_select_related = True

    def get_date_fermeture(self, obj):
        return date_format(obj.date_fermeture) if obj.date_fermeture else u''
    get_date_fermeture.short_description = u'Confirmation'

    def get_nom_region(self, obj):
        return obj.get_etablissement().region.nom
    get_nom_region.short_description = u'Région'

    def get_nom_prenom(self, obj):
        return obj.nom + ", " + obj.prenom
    get_nom_prenom.short_description = u'Nom du participant'

    def get_nom_etablissement(self, obj):
        return obj.get_etablissement().nom
    get_nom_etablissement.short_description = u'Établissement'

#    def get_total_paypal(self, obj):
#        return obj.get_etablissement()
#    get_total_paypal.short_description = u'Montant payé (€)'

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        ref = request.META.get('HTTP_REFERER', '')
        path = request.META.get('PATH_INFO', '')
        if not ref.split(path)[-1].startswith('?'):
            q = request.GET.copy()
            q['fermee__exact'] = '1'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(InscriptionAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def get_queryset(self, request):
        return Inscription.objects.filter(participant__id__isnull=True)\
            .select_related('invitation__etablissement__region')

    # def get_paiement_list_display(self, obj):
    #
    #     display = obj.get_paiement_display()
    #     if obj.paiement == 'CB':
    #         display += obj.statut_paypal_text()
    #     return display
    # get_paiement_list_display.short_description = u'Paiement'

    def response_change(self, request, obj):
        # on ne veut pas que l'utilisateur puisse valider l'inscription puis
        # continuer à l'éditer... et le bouton "enregistrer et continuer"
        # n'est pas facile à cacher...
        request.POST = request.POST.copy()
        if "_continue" in request.POST:
            del request.POST["_continue"]
        return super(InscriptionAdmin, self).response_change(request, obj)


class InvitationAdmin(ModelAdmin):
    search_fields = ('etablissement_nom', 'jeton', )
    list_display = (
        'etablissement_nom',
        'etablissement_id',
        'etablissement_region_id',
        'jeton',
        'enveloppe_id',
        'modele_id',
        'sud',
        'statut',
    )

    def __init__(self, *args, **kwargs):
        super(InvitationAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return obj is None

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Hotel, HotelAdmin)
admin.site.register(PointDeSuivi)
admin.site.register(TypeInstitutionSupplementaire)
admin.site.register(Activite)
admin.site.register(TypeFrais)
admin.site.register(ActiviteScientifique)
admin.site.register(InscriptionWeb, InscriptionAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Forfait)
