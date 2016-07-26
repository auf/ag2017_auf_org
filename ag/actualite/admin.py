# coding: utf8
from ag.outil.models import *
from ag.actualite.models import *
from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

class ActualiteAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['titre']}
    fieldsets = [
        ('Article', {'fields': ['status', 'date_pub', 'titre', 'slug', 'image', 'texte'], 'classes': ['wide']}),
    ]
    
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 60, 'rows': 24}, )},
    }
    
    def show_image2(self, obj):
        if obj.image:
            return "<img src='../../../media/%s' style='height:40px;'>" % obj.image
        else:
            return "<img src='../../../static/img/logo.jpg' style='height:40px;'>"
    show_image2.allow_tags = True #permet de sortir du html#
    show_image2.short_description = 'Image'

    list_display = ('status', 'show_image2', 'titre', 'date_pub')
    list_display_links = ('status', 'titre')
    search_fields = ['titre']

admin.site.register(Actualite, ActualiteAdmin)