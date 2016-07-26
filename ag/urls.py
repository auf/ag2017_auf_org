# -*- encoding: utf-8 -*
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^api/pong/', include('auf.django.pong.urls')),
    url(r'^contact/', 'ag.views.contact', name='contact'),
    url(r'^inscription/', include('ag.inscription.urls')),
    url(r'^gestion/', include('ag.gestion.urls')),
    url(r'^activites_scientifiques/',
        include('ag.activites_scientifiques.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^connexion/$', 'django.contrib.auth.views.login',
            {'template_name': 'login.html'}, name='connexion',
           ),
    url(r'^deconnexion/$', 'django.contrib.auth.views.logout_then_login',
        name='deconnexion'),
)

urlpatterns += patterns('',
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    (r'^tinymce/', include('tinymce.urls')),
)

urlpatterns += patterns('ag.views',
    (r'^$', 'accueil'),
    (r'^actualites/(?P<slug>[-\w]+)/$', 'actualite_detail'),
)

urlpatterns += patterns('',
    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True})
)
