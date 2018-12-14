from django.conf.urls import url, include
from django.contrib import admin
from shipanaro import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/', include('shipanaro.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^sso/', include('shipanaro.sso.urls')),
    url(r'^export_action/',
        include("export_action.urls", namespace="export_action")),
]
