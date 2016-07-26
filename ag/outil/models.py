from django.db import models

class Partenaire(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField(null=True, blank=True, upload_to='partenaire')
    lien = models.URLField()
    date_pub = models.DateField()
    
class Mot(models.Model):
    recteur = models.CharField(max_length=200)
    fonction = models.CharField(max_length=200)
    message = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to='mot')
    date_pub = models.DateField()
        
class Slider(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to='slider')
    titre = models.CharField(max_length=250)
    lien = models.CharField(max_length=200, null=True, blank=True)
    date_pub = models.DateField()
    
class Video(models.Model):
    titre = models.CharField(max_length=200)
    video = models.TextField(null=True, blank=True, verbose_name='Code de la video')
    description = models.TextField(null=True, blank=True, verbose_name='Description de la video')
    date_pub = models.DateField()