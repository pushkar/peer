from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^student/get/(?P<name>\w+)$', views.student, name='student'),
    url(r'^student/update/(?P<name>\w+)$', views.update_student, name='update_student'),
    url(r'^student/add/$', views.add_student, name='add_student'),
    url(r'^submission/add/$', views.add_submission, name='add_submission'),
    url(r'^review/add/$', views.add_review, name='add_review'),
    url(r'^review/update/$', views.update_review, name='update_review'),
    url(r'^review/get/$', views.get_review, name='get_review'),
    url(r'^codework/get/(?P<name>\w+)/(?P<username>\w+)$', views.codework, name='codework'),
    url(r'^codework/update/(?P<id>[0-9]+)$', views.update_codework, name='update_codework'),

]
