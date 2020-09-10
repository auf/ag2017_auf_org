# -*- encoding: utf-8 -*-
import sys

from ag.settings.base import *  # NOQA
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1']
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

if os.environ.get('DJDT', '0') == '1':
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)



#Décommentez ces lignes pour activer la debugtoolbar


# INTERNAL_IPS = ('127.0.0.1',)
# INSTALLED_APPS += ('debug_toolbar',)
#
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
# DEBUG_TOOLBAR_CONFIG = {
#    'INTERCEPT_REDIRECTS': False,
# }

AUTH_PASSWORD_REQUIRED = False
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
AG_INSCRIPTION_SENDER = 'beranger.enselme@auf.org'

TEMPLATES[0]['APP_DIRS'] = True
del TEMPLATES[0]['OPTIONS']['loaders']


SENDFILE_BACKEND="sendfile.backends.development"
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': True,
#    'handlers': {
#        'console': {
#            'level': 'DEBUG',
#            'class': 'logging.StreamHandler',
#            },
#    },
#    'loggers': {
#        'django.db.backends': {
#            'level': 'DEBUG',
#            'handlers': ['console'],
#        },
#    },
#}

SAML_AUTH = False
