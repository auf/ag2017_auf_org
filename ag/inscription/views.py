# encoding: utf-8
import collections
import datetime
import json
import time
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.dispatch import Signal
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import six

from ag.gestion import consts
from ag.inscription.models import (
    Inscription,
    Invitation,
    PaypalResponse,
    validate_pdt,
    is_ipn_valid,
    PaypalInvoice,
    get_forfaits)
from ag.inscription.forms import (
    AccueilForm,
    RenseignementsPersonnelsForm,
    ProgrammationForm,
    TransportHebergementForm,
    InscriptionForm,
    PaypalNotificationForm,
    PAYPAL_DATE_FORMATS
)

inscription_confirmee = Signal()

# noinspection PyUnresolvedReferences
import ag.gestion.notifications  # NOQA


def inscriptions_terminees():
    return datetime.date.today() >= settings.DATE_FERMETURE_INSCRIPTIONS


class Etape(object):

    def __init__(self, processus, donnees_etape):
        self.__dict__.update(donnees_etape)
        self.processus = processus

    def est_derniere_visible(self):
        return self.processus.est_derniere_visible(self)

    def est_derniere(self):
        return self.processus.est_derniere(self)

    def __str__(self):
        return '<etape %s>' % getattr(self, 'url_title', '?')

    def __unicode__(self):
        return self.__str__()


class EtapesProcessus(list):

    def __init__(self, donnees_etapes):
        super(EtapesProcessus, self).__init__(self)
        for donnees_etape in donnees_etapes:
            self.append(Etape(self, donnees_etape))

    def etape_par_url(self, url_title):
        for etape in self:
            if etape.url_title == url_title:
                return etape
        raise Http404('Aucune page ne porte le titre "%s".' % url_title)

    def etape_suivante(self, etape_courante):
        for etape in self:
            if etape.n == etape_courante.n + 1:
                return etape

    def est_derniere_visible(self, une_etape):
        for etape in self:
            if etape.n > une_etape.n and etape.tab_visible:
                return False
        return True

    def est_derniere(self, une_etape):
        for etape in self:
            if etape.n > une_etape.n:
                return False
        return True


def index(request):
    form = InscriptionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('processus_inscription', 'accueil')
    response = render(request, 'inscription/index.html', {
        'form': form,
    })
    request.session['django_language'] = 'fr'
    return response


def connexion_inscription(request, jeton):
    invitation = get_object_or_404(Invitation, jeton=jeton)
    try:
        inscription = Inscription.objects.get(invitation=invitation)
        if inscription.fermee or not inscriptions_terminees():
            request.session['inscription_id'] = inscription.id
        else:
            return redirect('inscriptions_terminees')
    except Inscription.DoesNotExist:
        if not inscriptions_terminees():
            inscription = Inscription(invitation=invitation)
            inscription.save()
            inscription.make_numero_dossier()
            request.session['inscription_id'] = inscription.id
        else:
            return redirect('inscriptions_terminees')
    return redirect('processus_inscription', 'accueil')


def get_paypal_context(request):
    return_url = getattr(
        settings, 'PAYPAL_RETURN_TEST_URL',
        request.build_absolute_uri(reverse('paypal_return')))
    return {
        'paypal_url': settings.PAYPAL_URL,
        'paypal_email_address': settings.PAYPAL_EMAIL_ADDRESS,
        'paypal_return_url': return_url,
        'paypal_notify_url':
            getattr(settings, 'PAYPAL_NOTIFY_TEST_URL', None) or
            request.build_absolute_uri(reverse('paypal_ipn')),
        'paypal_cancel_url': request.build_absolute_uri(
            reverse('paypal_cancel', args=('__invoice_uid__', ))),
    }


AppelEtapeProcessus = collections.namedtuple(
    'AppelEtapeProcessus',
    ('etapes_processus', 'etape_courante', 'request',
     'inscription'))

AppelEtapeResult = collections.namedtuple(
    'AppelEtapeResult', ('redirect', 'template_context', 'form_kwargs',
                         'etape_suivante'))


def redirect_etape(url_title):
    return redirect('processus_inscription', url_title)


def redirect_etape_suivante(appel_etape_processus):
    etapes_processus = appel_etape_processus.etapes_processus
    etape_courante = appel_etape_processus.etape_courante
    etape_suivante = etapes_processus.etape_suivante(etape_courante)
    return redirect('processus_inscription', etape_suivante.url_title)


def processus_inscription(request, url_title=None):
    etapes_processus = EtapesProcessus(donnees_etapes=ETAPES_INSCRIPTION)
    etape_courante = etapes_processus.etape_par_url(url_title)
    request.session['django_language'] = 'fr'
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('info_inscription')
    inscription = get_object_or_404(Inscription, id=inscription_id)
    if inscription.fermee:
        return redirect('dossier_inscription')

    appel_etape_processus = AppelEtapeProcessus(
        etapes_processus=etapes_processus, etape_courante=etape_courante,
        inscription=inscription, request=request)

    if etape_courante.func:
        etape_result = etape_courante.func(appel_etape_processus)
    else:
        etape_result = AppelEtapeResult(template_context=None, redirect=None,
                                        form_kwargs=None, etape_suivante=None)

    etape_suivante = etape_result.etape_suivante or \
        etapes_processus.etape_suivante(etape_courante)

    if etape_result.redirect:
        return etape_result.redirect

    context = {
        'inscription': inscription,
        'etape_courante': etape_courante,
        'etapes': etapes_processus,
    }
    if etape_result.template_context:
        context.update(etape_result.template_context)

    form_class = etape_courante.form_class
    if form_class:
        form = form_class(request.POST or None, instance=inscription,
                          **(etape_result.form_kwargs or {}))
        form.require_fields()
        if request.method == "POST" and form.is_valid():
            form.save()
            return redirect('processus_inscription', etape_suivante.url_title)
        context['form'] = form
    return render(request, 'inscription/' + etape_courante.template, context)


def apercu(appel_etape_processus):
    request = appel_etape_processus.request
    if request.method == 'POST':
        if 'modifier' in request.POST:
            redir = redirect_etape('participant')
        else:
            inscription = appel_etape_processus.inscription
            if not inscription.fermee:
                inscription.fermer()
                inscription_confirmee.send_robust(inscription)
            redir = redirect('dossier_inscription')
        return AppelEtapeResult(redirect=redir, template_context=None,
                                form_kwargs=None, etape_suivante=None)
    else:
        context = get_paypal_context(appel_etape_processus.request)
        context['montants'] = get_forfaits()
        return AppelEtapeResult(redirect=None, template_context=context,
                                form_kwargs=None, etape_suivante=None)


def renseignements_personnels(appel_etape_processus):
    """

    :param appel_etape_processus: AppelEtapeProcessus
    :return: AppelEtapeResult
    """
    inscription = appel_etape_processus.inscription
    initial = inscription.get_donnees_preremplir()
    return AppelEtapeResult(redirect=None, template_context=None,
                            form_kwargs={'initial': initial},
                            etape_suivante=None)


# noinspection PyUnusedLocal
def programmation(appel_etape_processus):
        inscription = appel_etape_processus.inscription
        total_programmation = inscription.get_total_programmation()
        infos_montants = get_forfaits()
        montant_inscription = infos_montants[consts.CODE_FRAIS_INSCRIPTION]\
            .montant
        if not inscription.prise_en_charge_possible():
            etape_suivante = appel_etape_processus.etapes_processus\
                .etape_par_url('apercu')
        else:
            etape_suivante = None
        return AppelEtapeResult(
            redirect=None,
            template_context={
                'total_programmation': total_programmation,
                'montant_frais_inscription': montant_inscription
            },
            form_kwargs={'infos_montants': infos_montants},
            etape_suivante=etape_suivante)


ETAPES_INSCRIPTION = (
    {
        "n": 0,
        "url_title": "accueil",
        "label": u"Accueil",
        "template": "accueil.html",
        "form_class": AccueilForm,
        "tab_visible": True,
        "func": None,
    },
    {
        "n": 1,
        "url_title": "participant",
        "label": u"Participant",
        "template": "participant.html",
        "form_class": RenseignementsPersonnelsForm,
        "tab_visible": True,
        "func": renseignements_personnels,
    },
    {
        "n": 2,
        "url_title": "programmation",
        "label": u"Programmation",
        "template": "programmation.html",
        "form_class": ProgrammationForm,
        "tab_visible": True,
        "func": programmation,
    },
    {
        "n": 3,
        "url_title": "transport-hebergement",
        "label": u"Séjour",
        "template": "transport_hebergement.html",
        "form_class": TransportHebergementForm,
        "tab_visible": True,
        "func": None,
    },
    {
        "n": 4,
        "url_title": "apercu",
        "label": u"Aperçu",
        "template": "apercu.html",
        "form_class": None,
        "tab_visible": True,
        "func": apercu,
    },
)


@require_GET
def calcul_frais_programmation(request):
    inscription = Inscription(accompagnateur=True)
    form = ProgrammationForm(request.GET, instance=inscription,
                             infos_montants=get_forfaits())
    form.is_valid()
    total = form.instance.get_total_programmation()
    return HttpResponse(str(int(total)))


def get_inscription_by_invoice_uid(invoice_uid):
    invoice = PaypalInvoice.objects.select_related('inscription')\
        .get(invoice_uid=invoice_uid)
    return invoice.inscription, invoice.invoice_uid


def paypal_return(request):
    # tx=9TN773664V3684442&st=Pending&amt=570.00&cc=EUR&cm=&item_number=
    tx = request.GET.get('tx')
    paypal_response = PaypalResponse.objects.create(
        type_reponse='PDT', txn_id=tx,
        request_data=getattr(request, request.method).urlencode())

    validation_response = validate_pdt(tx)
    invoice_uid_str = validation_response.response_dict.get('invoice', None)
    inscription, invoice_uid = get_inscription_by_invoice_uid(invoice_uid_str)
    paypal_response.validated = validation_response.valid
    paypal_response.validation_response_data = validation_response.raw_response
    paypal_response.invoice_uid = invoice_uid
    paypal_response.inscription = inscription
    paypal_response.save()
    if paypal_response.validated:
        d = validation_response.response_dict
        dict_to_paypal_response(d, paypal_response)
        paypal_response.save()
    return redirect('dossier_inscription')


def dict_to_paypal_response(paypal_dict, paypal_response):
    paypal_response.montant = paypal_dict.get('mc_gross')
    paypal_response.devise = paypal_dict.get('mc_currency')
    paypal_response.statut = paypal_dict.get('payment_status')
    paypal_response.raison_attente = paypal_dict.get('pending_reason')
    paypal_response.date_heure = paypal_dict.get('payment_date')
    payment_date = paypal_dict.get('payment_date')
    if isinstance(payment_date, six.string_types):
        for date_format in PAYPAL_DATE_FORMATS:
            try:
                paypal_response.date_heure = datetime.datetime(
                    *time.strptime(payment_date, date_format)[:6]
                )
            except ValueError:
                continue
    else:
        paypal_response.date_heure = payment_date


@csrf_exempt
@transaction.non_atomic_requests
def paypal_ipn(request):
    form = PaypalNotificationForm(request.POST)
    paypal_response = PaypalResponse.objects.create(
        type_reponse='IPN', request_data=request.body)
    if form.is_valid():
        txn_id = form.cleaned_data['txn_id']
        invoice_uid_str = form.cleaned_data['invoice']
        inscription, inv_uid = get_inscription_by_invoice_uid(invoice_uid_str)
        paypal_response.txn_id = txn_id
        paypal_response.invoice_uid = inv_uid
        paypal_response.inscription = inscription
        dict_to_paypal_response(form.cleaned_data, paypal_response)
    paypal_response.save()
    valid, validation_response = is_ipn_valid(request)
    paypal_response.validated = valid
    paypal_response.validation_response_data = validation_response
    paypal_response.save()
    return HttpResponse("OK")


def paypal_cancel(request, invoice_uid):
    inscription, invoice_uid = get_inscription_by_invoice_uid(invoice_uid)
    PaypalResponse.objects.create(
        invoice_uid=invoice_uid, inscription=inscription,
        type_reponse='CAN',
    )
    return redirect('dossier_inscription')


@require_POST
def make_paypal_invoice(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return HttpResponse(status=401)
    inscription = Inscription.objects.get(id=inscription_id)
    inscription.paiement = 'CB'
    if not inscription.fermee:
        inscription.fermer()
        inscription_confirmee.send_robust(inscription)
    inscription.save()
    invoice = PaypalInvoice.objects.create(inscription=inscription,
                                           montant=inscription.get_total_du())
    return HttpResponse(str(invoice.invoice_uid))
