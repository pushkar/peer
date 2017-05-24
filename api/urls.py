from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^student/get/(?P<username>\w+)$', views.student, name='student'),
    url(r'^assignment/get/(?P<a_name>\w+)$', views.assignment, name='assignment'),
    url(r'^codework/get/(?P<a_name>\w+)/(?P<username>\w+)$', views.codework, name='codework'),
    url(r'^codework/update/(?P<id>[0-9]+)$', views.update_codework, name='update_codework'),

]
