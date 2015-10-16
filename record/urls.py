from django.conf.urls import patterns, url

from record import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^form/(?P<group>[0-9]+)$', views.form, name='form'),
    url(r'^update$', views.update, name='update'),
)
