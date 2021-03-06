from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^profile/', views.edit_profile, name='profile'),
    url(r'^players/$', views.players, name='players'),
    url(r'^about/$', views.about, name='about'),
    url(r'^create/$', views.create_tournament, name='create'),
    url(r'^delete/(?P<tournament_id>[0-9]+)/$', views.delete_tournament, name='delete'),
    url(r'^generate/(?P<tournament_id>[0-9]+)/$', views.create_teams, name='generate'),
    url(r'^(?P<tournament_name>[\w\s]+)/$', views.tournament, name='tournament'),
    url(r'^(?P<tournament_name>[\w\s]+)/(?P<stage_id>[0-9]+)/$', views.table, name='table'),
    url(r'^(?P<tournament_name>[\w\s]+)/matches/(?P<stage_id>[0-9]+)/$', views.create_matches, name='matches'),
    url(r'^(?P<tournament_name>[\w\s]+)/(?P<stage_id>[0-9]+)/match-list/$', views.show_matches, name='show'),
]
