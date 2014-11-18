from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'^student/(?P<var>\w+)/(?P<val>\w+)$', views.student, name='student'),
    url(r'^(?P<exam>\w+)/tflog/(?P<q_id>\w+)$', views.tflog, name='tflog'),
    url(r'^(?P<exam>\w+)/mclog/(?P<q_id>\w+)$', views.mclog, name='mclog'),
    url(r'^(?P<exam>\w+)/selog/(?P<q_id>\w+)$', views.selog, name='selog'),
    url(r'^(?P<exam>\w+)/q/all$', views.question_all, name='question_all'),
    url(r'^(?P<exam>\w+)/q/(?P<q_id>\w+)$', views.question, name='question'),


    url(r'^student/all$', views.student_all, name='student_all'),

    url(r'^(?P<exam>\w+)/answer/all$', views.answer_all, name='answer_all'),

    url(r'^$', views.index, name='index'),
)
