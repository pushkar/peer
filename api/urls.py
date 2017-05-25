from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^student/all$', views.student_all, name='student_all'),
    url(r'^student/add$', views.student_add, name='student_add'),
    url(r'^student/user/(?P<username>\w+)$', views.student_by_user, name='student_by_user'),
    url(r'^student/id/(?P<id>[0-9]+)$', views.student_by_id, name='student_by_id'),
    url(r'^assignment/all$', views.assignment_all, name='assignment_all'),
    url(r'^assignment/shortname/(?P<a_name>\w+)$', views.assignment, name='assignment'),
    url(r'^codework/get/(?P<a_name>\w+)/(?P<username>\w+)$', views.codework, name='codework'),
    url(r'^codework/user/(?P<username>\w+)$', views.codework_by_username, name='codework_by_username'),
    url(r'^codework/assignment/(?P<a_name>\w+)$', views.codework_by_assignment, name='codework_by_assignment'),
    url(r'^codepair/id/(?P<id>[0-9]+)$', views.codepair, name='codepair'),
]
