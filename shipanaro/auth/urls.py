from django.conf.urls import url
from shipanaro.auth import views

urlpatterns = [
    url('^login/$', views.login, name='login'),
    url('^logout/$', views.logout, name='logout'),
    url('^password/reset/$', views.password_reset, name='password_reset'),
    url('^password/reset/done/$',
        views.password_reset_done,
        name='password_reset_done'),
    url('^password/reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$',
        views.password_reset_confirm,
        name='password_reset_confirm'),
    url('^password/reset/complete/$',
        views.password_reset_complete,
        name='password_reset_complete'),
    url('^profile/$', views.membership, name='profile'),
]
