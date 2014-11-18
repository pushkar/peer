from django.conf.urls import patterns, url

from recommender import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
