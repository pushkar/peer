from django.conf.urls import patterns, url

from record import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add$', views.add, name='add'),
    url(r'^form$', views.form, name='form'),

)
