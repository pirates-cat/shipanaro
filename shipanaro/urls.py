from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from shipanaro import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^accounts/", include("shipanaro.auth.urls")),
    url(r"^__capitania__/", admin.site.urls),
    url(r"^sso/", include("shipanaro.sso.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
