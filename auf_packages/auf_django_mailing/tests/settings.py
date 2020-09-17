# -*- encoding: utf-8 -*-



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'auf_django_mailing',
    'tests'
    )

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

MAILING_MODELE_PARAMS_ENVELOPPE = 'tests.FakeEnveloppeParams'
MAILING_TEMPORISATION = 0

SECRET_KEY = 'not-secret'

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            # ... some options here ...
        },
    },
]
