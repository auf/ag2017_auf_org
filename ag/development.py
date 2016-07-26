# -*- encoding: utf-8 -*-
import sys

from ag.settings import *  # NOQA
DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += ('django_nose',)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

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

if 'test' in sys.argv or 'bin/test' in sys.argv:
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

PAYPAL_EMAIL_ADDRESS = 'berang_1344607404_biz@auf.org'
PAYPAL_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_PDT_TOKEN = 'wYHr_XQJY0ShuRgxcunh7_MP99VLew-DYonAmJi8rGtNRTiUDotFfkgN_UC'

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