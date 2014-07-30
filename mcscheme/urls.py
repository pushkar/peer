from django.conf.urls import patterns, url

from mcscheme import views

urlpatterns = patterns('',
    url(r'^exam/$', views.exam, name='exam'),
    url(r'^db/populate/$', views.db_populate, name='db_populate'),
    url(r'^db/show/$', views.db_show, name='db_show'),
    url(r'^$', views.index, name='index'),
)
