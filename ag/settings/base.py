# -*- encoding: utf-8 -*-
import os
import socket
import datetime

# Rapports d'erreurs
SERVER_EMAIL = 'ne-pas-repondre@auf.org'
EMAIL_SUBJECT_PREFIX = '[auf_ag - %s] ' % socket.gethostname()
ADMINS = ()
MANAGERS = ADMINS


TIME_ZONE = 'America/Montreal'

LANGUAGE_CODE = 'fr'
gettext = lambda x: x
USE_L10N = True

SITE_ID = 1

CMS_LANGUAGES = {
    1: [
        {
            'code': 'fr',
            'name': gettext('French'),
        }
    ]
}

DEFAULT_LANGUAGE = 1

DATE_INPUT_FORMATS = ('%d/%m/%Y', '%Y-%m-%d')
DATE_FORMAT = 'j N Y'
SHORT_DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'

PROJECT_ROOT = os.path.dirname(__file__)
SITE_ROOT = os.path.dirname(PROJECT_ROOT)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(SITE_ROOT, 'sitestatic')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'static'),)

ROOT_URLCONF = 'ag.urls'

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'auf.django.permissions',
    'auf_django_mailing',
    'ag.reference',
    'ag.core',
    'ag.inscription',
    'ag.gestion',
    'ag.dossier_inscription',
    'ag.outil',
    'ag.actualite',
    'ag.activites_scientifiques',
    'ag.elections',
    'raven.contrib.django',
    
    'crispy_forms',
    'sekizai',
    'treebeard',

    'filer',
    'djangocms_text_ckeditor',
    'easy_thumbnails',
    'djangocms_link',
    'cms',
    'menus',
    'tinymce',
    )


MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ag.FrenchAdminMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # /'auf.django.piwik.middleware.TrackMiddleware',
    'auf.django.permissions.middleware.PermissionDeniedMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',    
    'cms.middleware.toolbar.ToolbarMiddleware',      
    'django.middleware.cache.FetchFromCacheMiddleware',
    )


CMS_TEMPLATES = (
    ('accueil.html', gettext('Page Accueil')),
    ('page.html', gettext('Page Texte')),
    ('page_sous_rubrique.html', gettext('Page sous rubrique')),
    ('mot.html', gettext('Page Mot de recteur')),
    ('partenaire.html', gettext('Page Partenaire')),
    ('page_actu.html', gettext('Page Actualité')),
    ('video.html', gettext('Page Vidéo')),
    ('ateliers-scientifiques.html', gettext('Page Accueil ateliers')),
    ('atelier.html', gettext('Page atelier')),
)


ADMIN_TOOLS_INDEX_DASHBOARD = 'project.dashboard.CustomIndexDashboard'

MAILING_MODELE_PARAMS_ENVELOPPE = 'inscription.InvitationEnveloppe'
MAILING_TEMPORISATION = 2

AUTH_PROFILE_MODULE = 'core.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'auf.django.permissions.AuthenticationBackend',
    )
LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/gestion/'

CRISPY_TEMPLATE_PACK = 'uni_form'

PATH_FICHIERS_PARTICIPANTS = os.path.join(SITE_ROOT, 'medias_participants')
GESTION_AG_SENDER = 'ag2017@auf.org'

SENDFILE_BACKEND = 'sendfile.backends.simple'

FILER_CANONICAL_URL = 'permanent/'

ROLE_PROVIDERS = ('ag.gestion.role_provider', )

from .conf import *  # NOQA

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'theme_advanced_buttons1' : "formatselect,|,bold,italic,underline,|,bullist,numlist,|,undo,redo,|,link,unlink,image,|,backcolor,|removeformat,visualaid,code,",
    'theme_advanced_buttons2' : "",
    'theme_advanced_buttons3' : "",
    'theme_advanced_statusbar_location' : "bottom",
    'theme_advanced_toolbar_align' : "left",
    'width' : "800",
    'height' : "360",
    'theme_advanced_resizing' : "true",
    'custom_undo_redo_levels': 10,
    'theme_advanced_toolbar_location' : 'top',
}

DATE_FERMETURE_INSCRIPTIONS = datetime.date(2018, 3, 22)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'ag/templates'
        ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'ag.outil.context_processors.list_Video',
                'ag.outil.context_processors.list_Video2',
                'ag.outil.context_processors.list_mot1',
                'ag.outil.context_processors.list_mot2',
                'ag.outil.context_processors.list_partenaire',
                'ag.outil.context_processors.list_slider',
                'ag.outil.context_processors.list_actu',
            ],
            'loaders': [('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ])],
        },
    },
]
