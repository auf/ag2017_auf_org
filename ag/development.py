# -*- encoding: utf-8 -*-
import sys

from ag.settings import *  # NOQA
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

if os.environ.get('DJDT', '0') == '1':
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)



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

if 'test' in sys.argv or 'pytest_teamcity' in sys.argv or \
                'py.test' in sys.argv[0]:
    AUF_REFERENCES_MANAGED = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ag_dev',
            'HOST' : '/var/run/mysqld/mysqld-ram.sock',
            'USER': 'root',
            'PORT' : '65432',
            'OPTIONS': {
                "init_command": "SET storage_engine=INNODB",
            },
        }
    }
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    MAILING_TEMPORISATION = 0
    LOGGING = {
        'version': 1,
        'handlers': {
            'file': {
                'level': 'CRITICAL',
                'class': 'logging.FileHandler',
                'filename': '/tmp/codesy-debug.log',
            },
        },
        'loggers': {
            'django.db.backends.schema': {
                'handlers': ['file'],
                'propagate': True,
                'level': 'CRITICAL',
            },
            '': {
                'handlers': ['file'],
                'level': 'CRITICAL',
            }
        }
    }

    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "notmigrations"

    MIGRATION_MODULES = DisableMigrations()
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
else:
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
