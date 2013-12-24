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
    url(r'^trails/$', views.Trails_Trails),
    url(r'^trails/getpossibleentrypoints/$', views.Trails_GetPossibleEntryPoints),
    url(r'^map/trail/(\d+)/$', views.Map_ViewTrailById),
    url(r'^map/trail/(\d+)/(\d+)/$', views.Map_ViewTrailById),
    url(r'^map/trailbynum/(\d+)/(\d+)/$', views.Map_ViewTrailByPanoNum),
    url(r'^map/requestmoredata/$', views.Map_RequestMoreData),
    url(r'^map/getpointofinterest$', views.Map_GetPointOfInterest),
    url(r'^pois/$', views.PoI_ListAll),
    url(r'^pois/atmospherics/$', views.PoI_Atmospherics),
    url(r'^pois/fauna/$', views.PoI_Fauna),
    url(r'^pois/flora/$', views.PoI_Flora),
    url(r'^pois/landmarks/$', views.PoI_Landmarks),
)
