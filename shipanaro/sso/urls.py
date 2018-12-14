from django.conf.urls import url
from shipanaro.sso import views

urlpatterns = [
    url('^login/$', views.login, name='sso_login'),
    url('^auth/$', views.authorize, name='sso_auth'),
]
