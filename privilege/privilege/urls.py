from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from core.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    
    url(r'^', include('auth.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),

    url(r'^$', RedirectView.as_view(url='/dashboard', permanent=False)),
    url(r'^home$', RedirectView.as_view(url='/dashboard', permanent=False)),
    
    url(r'^dashboard$', view_dashboard, name='dashboard'),
    
    url(r'^account', view_privilege, name='account'),
    
    url(r'^faculty/list$', view_faculty_list, name='faculty_list'),
    #url(r'^faculty/create$', view_faculty_form, name='faculty_create'),
    url(r'^faculty/(?P<id>\d+)$', view_faculty_info, name='faculty_info'),
    #url(r'^faculty/(?P<id>\d+)/edit$', view_faculty_form, name='faculty_edit'),
    url(r'^faculty/(?P<id>\d+)/delete$', view_faculty_delete, name='faculty_delete'),
    
    url(r'^project/list$', view_project_list, name='project_list'),
    #url(r'^project/create$', view_project_form, name='project_create'),
    url(r'^project/(?P<id>\d+)$', view_project_info, name='project_info'),
    #url(r'^project/(?P<id>\d+)/edit$', view_project_form, name='project_edit'),
    url(r'^project/(?P<id>\d+)/delete$', view_project_delete, name='project_delete'),
    
    url(r'^request/list$', view_request_list, name='request_list'),
    #url(r'^request/create$', view_request_form, name='request_create'),
    url(r'^request/(?P<id>\d+)$', view_request_info, name='request_info'),
    #url(r'^request/(?P<id>\d+)/edit$', view_request_form, name='request_edit'),
    url(r'^request/(?P<id>\d+)/delete$', view_request_delete, name='request_delete'),
    url(r'^request/(?P<id>\d+)/activate$', view_request_activate, name='request_activate'),
    url(r'^request/(?P<id>\d+)/approve$', view_request_approve, name='request_approve'),
    url(r'^request/(?P<id>\d+)/reject$', view_request_reject, name='request_reject'),
    
    url(r'^faculty/(?P<id>\d+)/create', view_faculty_create_project, name='faculty_create_project'),
    url(r'^project/(?P<id>\d+)/request$', view_project_create_request, name='project_create_request'),
    
    url(r'^history$', view_history, name='project_list'),
    
    url(r'^user/(?P<id>\d+)$', view_user_info, name='user_info'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
