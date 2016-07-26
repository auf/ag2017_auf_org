# coding: utf8
from ag.outil.models import *
from django.contrib import admin
from django.db import models

class PartenaireAdmin(admin.ModelAdmin):
        
    def show_image(self, obj):
      return "<img src='../../../media/%s' style='height:90px;'>" % obj.image
    show_image.allow_tags = True #permet de sortir du html#
    show_image.short_description = 'Image'
        
    list_display = ('nom', 'show_image', 'lien', 'date_pub')
    
class MotAdmin(admin.ModelAdmin):
        
    def show_image(self, obj):
      return "<img src='../../../media/%s' style='height:90px;'>" % obj.image
    show_image.allow_tags = True #permet de sortir du html#
    show_image.short_description = 'Image'
        
    list_display = ('recteur', 'fonction', 'show_image', 'message', 'date_pub')

class SliderAdmin(admin.ModelAdmin):
        
    def show_image(self, obj):
      return "<img src='../../../media/%s' style='height:90px;'>" % obj.image
    show_image.allow_tags = True #permet de sortir du html#
    show_image.short_description = 'Image'
        
    list_display = ('titre','show_image',  'lien', 'date_pub')
    
class VideoAdmin(admin.ModelAdmin):
        
    list_display = ('titre', 'date_pub')

admin.site.register(Partenaire, PartenaireAdmin)
admin.site.register(Mot, MotAdmin)
admin.site.register(Slider, SliderAdmin)
admin.site.register(Video, VideoAdmin)