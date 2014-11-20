from django.conf.urls import patterns, url

from recommender import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^leaderboard$', views.leaderboard, name='leaderboard'),
    url(r'^overview$', views.overview, name='overview'),
    url(r'^dataset$', views.dataset, name='dataset'),
    url(r'^prediction$', views.submit_prediction, name='submit_prediction'),
    url(r'^report$', views.submit_report, name='submit_report'),
    url(r'^review$', views.submit_review, name='submit_review'),
    url(r'^populate$', views.populate, name='populate'),
)
