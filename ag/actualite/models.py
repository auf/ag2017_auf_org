from django.db import models    

class Actualite(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    texte = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to='actualite')
    date_pub = models.DateField()
    date_mod = models.DateTimeField('date de derniere modification', auto_now_add=True)
    status = models.CharField(max_length=1, null=False, default='3', blank=False, choices=(('1', 'En cours de redaction'), ('2', 'Propose a la publication'), ('3', 'Publie en Ligne'), ('4', 'A supprimer')))
    
    class Meta:
        ordering = ('-date_pub',)
    
    def __str__(self):
        return self.titre  

    def get_absolute_url(self):
        return "/actualites/%s/" %self.slug