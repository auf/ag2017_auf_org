#!/usr/bin/env python
import os
import sys

SITE_ROOT = os.path.dirname(__file__)

sys.path.append(os.path.join(SITE_ROOT, '../auf-django-sdk/sdk/django18_auf/'))
sys.path.append(os.path.join(SITE_ROOT, '../auf-django-sdk/sdk/django18_base/'))
sys.path.append(os.path.join(SITE_ROOT, '../auf-django-sdk/sdk/django18_dev/'))
sys.path.append(os.path.join(SITE_ROOT, '../auf-django-sdk/sdk/django18_auf_dev/'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ag.settings")

    from django.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
