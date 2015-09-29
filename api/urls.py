from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^student/get/(?P<name>\w+)$', views.student, name='student'),
    url(r'^student/add/$', views.add_student, name='add_student'),
    url(r'^submission/add/$', views.add_submission, name='add_submission'),
    #url(r'^(?P<a_name>\w+)/$', views.home, name='home'),
)
