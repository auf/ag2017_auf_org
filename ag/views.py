from ag import settings
from actualite.models import Actualite
from django.core.mail import EmailMessage
from django.forms import Form, CharField
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.template import Context, RequestContext

class ContactForm(Form):
    username = CharField(required=True, label=u"Nom")
    usermail = CharField(required=True, label=u"Adresse E-mail")
    usersite = CharField(required=False, label=u"Site Internet")
    subject = CharField(required=False, label=u"Sujet")
    message = CharField(label=u"Message", required=True)


def contact(request):
    if request.method == 'GET':
        return render(request, 'contact.html')
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            message = EmailMessage()
            message.subject = u"ag2013 web contact - "\
                              + form.cleaned_data['subject']
            message.body = u"Nom: " + form.cleaned_data['username'] + u"\r" +\
                u"Adresse E-Mail: " + form.cleaned_data['usermail'] + u"\r" +\
                u"Site internet: " + form.cleaned_data['usersite'] + u"\r" +\
                u"Sujet: " + form.cleaned_data['subject'] + u"\r" +\
                u"Message: " + form.cleaned_data['message'] + u"\r"
            message.to = ['ag2013@auf.org']
            message.from_email = form.cleaned_data['usermail']
            message.send(fail_silently=True)
            return redirect('/')
        else:
            print form.errors
            return render(request, 'contact.html', { 'form': form })

def accueil(request):
    if request.GET.get('langue'):
        langue = request.GET['langue']
    else:
        langue = 'francais'
    return render_to_response('index.html', {'langue': langue}, context_instance = RequestContext(request))

def actualite_detail(request, slug):
    p = get_object_or_404(Actualite, slug=slug)
    return render_to_response('page_actu_detail.html', {'actualite': p,'page_slug': 'actualites/', 'page_title': 'Actualite'}, context_instance = RequestContext(request))