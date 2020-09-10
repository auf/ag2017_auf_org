# -*- encoding: utf-8 -*-
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


def role_provider(user):
    """
    Cible pour le setting ROLE_PROVIDERS.
    """
    if user.is_anonymous():
        return []
    else:
        return user.roles.all()


class FrenchAdminMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.path.startswith('/admin/') or \
           request.path.startswith('/gestion/'):
            request.LANGUAGE_CODE = 'fr'
            translation.activate('fr')
