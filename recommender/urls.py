from django.conf.urls import patterns, url

from recommender import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^leaderboard$', views.leaderboard, name='leaderboard'),
    url(r'^prediction$', views.submit_prediction, name='submit_prediction'),
    url(r'^populate$', views.populate, name='populate'),
)
