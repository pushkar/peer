from django.conf.urls import patterns, url

from record import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^details/(?P<type>\w*)$', views.details, name='details'),
    url(r'^form/(?P<student>\w+)/(?P<group>\w+)$', views.form, name='form'),
    url(r'^update/(?P<student>\w+)$', views.update, name='update'),
)
