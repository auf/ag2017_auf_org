# -*- encoding: utf-8 -*-

import os

APP_ROOT = os.path.dirname(__file__)


def role_provider(user):
    """
    Cible pour le setting ROLE_PROVIDERS.
    """
    if user.is_anonymous():
        return []
    else:
        return user.roles.all()
