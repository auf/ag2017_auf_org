from ag import settings
from .actualite.models import Actualite
from django.core.mail import EmailMessage
from django.forms import Form, CharField
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.template import Context, RequestContext

class ContactForm(Form):
    username = CharField(required=True, label="Nom")
    usermail = CharField(required=True, label="Adresse E-mail")
    usersite = CharField(required=False, label="Site Internet")
    subject = CharField(required=False, label="Sujet")
    message = CharField(label="Message", required=True)


def contact(request):
    if request.method == 'GET':
        return render(request, 'contact.html')
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            message = EmailMessage()
            message.subject = "ag2017 web contact - "\
                              + form.cleaned_data['subject']
            message.body = "Nom: " + form.cleaned_data['username'] + "\r" +\
                "Adresse E-Mail: " + form.cleaned_data['usermail'] + "\r" +\
                "Site internet: " + form.cleaned_data['usersite'] + "\r" +\
                "Sujet: " + form.cleaned_data['subject'] + "\r" +\
                "Message: " + form.cleaned_data['message'] + "\r"
            message.to = ['ag2017@auf.org']
            message.from_email = form.cleaned_data['usermail']
            message.send(fail_silently=True)
            return redirect('/')
        else:
            print(form.errors)
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