# -*- encoding: utf-8 -*
import os

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout_then_login
from ag.views import contact, actualite_detail, accueil

admin.autodiscover()

urlpatterns = [
    url(r'^contact/', contact, name='contact'),
    url(r'^inscription/', include('ag.inscription.urls')),
    url(r'^dossier_inscription/', include('ag.dossier_inscription.urls')),
    url(r'^gestion/', include('ag.gestion.urls')),
    url(r'^gestion/elections/', include('ag.elections.urls')),
    url(r'^activites_scientifiques/', include('ag.activites_scientifiques.urls')),
    url(r'^admin/', admin.site.urls),
    url(
        r'^connexion/$', login,
        {'template_name': 'login.html'}, name='connexion',
    ),
    url(r'^deconnexion/$', logout_then_login,
        name='deconnexion'),
]

urlpatterns += [
    url(r'^tinymce/', include('tinymce.urls')),
]

urlpatterns += [
    url(r'^filer/', include('filer.urls')),
]

urlpatterns += [
    url(r'^$', accueil, name='accueil'),
    url(r'^actualites/(?P<slug>[-\w]+)/$', actualite_detail),
]

# if settings.SAML_AUTH:
#     urlpatterns += patterns(
#         '',
#         (r'^', include('auf.django.saml.urls')),
#     )
# else:
#     urlpatterns += patterns(
#             '',
#             (r'^', include('auf.django.saml.mellon_urls')),
#     )

urlpatterns += [
    url(r'^', include('cms.urls')),
]

# if not settings.SAML_AUTH:
#     urlpatterns += patterns(
#             '',
#             (r'^', include('auf.django.saml.mellon_urls')),
#     )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()  # NOQA
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True})
    ]

    if os.environ.get('DJDT', '0') == '1':
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
