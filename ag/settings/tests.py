# noinspection PyUnresolvedReferences
from ag.settings.base import *

AUF_REFERENCES_MANAGED = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ag_dev',
        'HOST': '127.0.0.1',
        'USER': 'root',
        'PASSWORD': 'drowssap',
        'PORT': '3344',
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
        return None


MIGRATION_MODULES = DisableMigrations()
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


AUTH_PASSWORD_REQUIRED = False
AG_INSCRIPTION_SENDER = 'beranger.enselme@auf.org'
SENDFILE_BACKEND="sendfile.backends.development"
SAML_AUTH = False

DESTINATAIRES_NOTIFICATIONS = {
    'service_institutions': ['benselme@gmail.com'],
    'finance': ['benselme@gmail.com'],
    'bureau_missions': ['benselme@gmail.com'],
    'inscription': ['benselme@gmail.com'],
    'gestion': ['benselme@gmail.com'],
}
