from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^$', 'core.views.home', name='home'),
    url(r'^', include('auth.urls')),
    url(r'^home/$', 'core.views.dashboard', name='dashboard'),
    url(r'^project/$', 'core.views.project', name='project'),
    url(r'^faculty/$', 'core.views.faculty', name='faculty'),
    url(r'^view/projects/$', "core.views.projectList", name='projectList'),
    url(r'^view/faculties/$', "core.views.facultyList", name='facultyList'),
    # url(r'^privilege/', include('privilege.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
