from django.conf.urls import patterns, url

from student import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^populate$', views.populate, name='populate'),
)
