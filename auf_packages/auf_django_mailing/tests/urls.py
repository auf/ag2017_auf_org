from django.conf.urls import url
from .views import dummy

urlpatterns = [
    url(r'^acces/(?P<jeton>\w+)$', dummy, name='dummy'),
]

