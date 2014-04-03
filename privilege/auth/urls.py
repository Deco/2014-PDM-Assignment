from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',

    url('^login/$',
        login,
        {'template_name': 'login.html'},
        name='login'
        ),

    url('^logout/$',
        logout,
        {'next_page': '/'},
        name='logout'
        ),

)
