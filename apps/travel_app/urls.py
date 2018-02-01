from django.conf.urls import url
from . import views
urlpatterns = [
  url(r'^$', views.index),
  url(r'^register$', views.register),
  url(r'^login$', views.login),
  url(r'^logout$', views.logout),
  url(r'^travels$', views.travels),
  url(r'^travels/new$', views.travels_new),
  url(r'^travels/join$', views.travels_join),
  url(r'^travels/create$', views.travels_create),
  url(r'^travels/destination/(?P<id>\d+)$', views.destination),
]
