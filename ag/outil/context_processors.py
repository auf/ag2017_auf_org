from ag.outil.models import *
from ag.actualite.models import *
    
def list_Video(request):
    list = Video.objects.all().order_by('?')[:1]
    return {
        'video_list' : list
    }
    
def list_Video2(request):
    list = Video.objects.all().order_by('-date_pub')
    return {
        'video_list2' : list
    }
    
def list_mot1(request):
    list = Mot.objects.all().order_by('-date_pub')
    return {
        'mot_list1' : list
    }
    
def list_mot2(request):
    list = Mot.objects.all().order_by('?')[:1]
    return {
        'mot_list2' : list
    }
    
def list_partenaire(request):
    list = Partenaire.objects.all().order_by('-date_pub')
    return {
        'partenaire_list' : list
    }
    
def list_slider(request):
    list = Slider.objects.all().order_by('-date_pub')
    return {
        'slider_list' : list
    }
    
def list_actu(request):
    list = Actualite.objects.all().order_by('-date_pub')
    return {
        'actu_list' : list
    }