from django.conf.urls import patterns, include, url
from trailview import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trailview.views.home', name='home'),
    # url(r'^trailview/', include('trailview.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.Home_Home),
    url(r'^Trails/$', views.Trails_Trails),
    url(r'^Trails/GetPossibleEntryPoints/(\d+)/(\w+)$', views.Trails_GetPossibleEntryPoints),
    url(r'^Map/Trail/(\d+)/', views.Map_ViewTrailById),
    url(r'^Map/Trail/(\d+)/(\d+)/$', views.Map_ViewTrailStartingAtPano),
)
