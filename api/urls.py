from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'^student/(?P<var>\w+)/(?P<val>\w+)$', views.student, name='student'),
    url(r'^tflog/(?P<q_id>\w+)$', views.tflog, name='tflog'),
    url(r'^mclog/(?P<q_id>\w+)$', views.mclog, name='mclog'),

    url(r'^student/all$', views.student_all, name='student_all'),
    url(r'^question/all$', views.question_all, name='question_all'),
    url(r'^answer/all$', views.answer_all, name='answer_all'),

    url(r'^$', views.index, name='index'),
)
