from django.conf.urls import url, include
from django.contrib import admin
from shipanaro.api.users import UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # url(r'^user/', include('django.contrib.auth.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    # Browsable API disabled.
    # url(r'^api/auth/', include(
    #    'rest_framework.urls', namespace='rest_framework')),
]
