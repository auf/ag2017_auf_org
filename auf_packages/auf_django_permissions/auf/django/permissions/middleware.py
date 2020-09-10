import urlparse
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.utils.deprecation import MiddlewareMixin


class PermissionDeniedMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            if request.user.is_anonymous:

                # Code de redirection venant de
                # django.contrib.auth.decorators.permission_required()
                path = request.build_absolute_uri()
                login_url = settings.LOGIN_URL
                # If the login url is the same scheme and net location then
                # just use the path as the "next" url.
                login_scheme, login_netloc = urlparse.urlparse(login_url)[:2]
                current_scheme, current_netloc = urlparse.urlparse(path)[:2]
                if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                    path = request.get_full_path()
                return redirect_to_login(path, login_url, 'next')
            else:
                return HttpResponseForbidden(render_to_string('403.html'))
        else:
            return None
