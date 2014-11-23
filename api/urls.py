from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'^student/(?P<var>\w+)/(?P<val>\w+)$', views.student, name='student'),
    url(r'^(?P<exam>\w+)/tflog/q/(?P<q_id>\d+)$', views.tflog, name='tflog'),
    url(r'^(?P<exam>\w+)/mclog/q/(?P<q_id>\d+)$', views.mclog, name='mclog'),
    url(r'^(?P<exam>\w+)/selog/q/(?P<q_id>\d+)$', views.selog, name='selog'),
    url(r'^(?P<exam>\w+)/q/all$', views.question_all, name='question_all'),
    url(r'^(?P<exam>\w+)/q/(?P<q_id>\w+)$', views.question, name='question'),

    url(r'^(?P<exam>\w+)/(?P<log>\w+)/id/(?P<id>\d+)/score/(?P<score>\d+.\d+)$', views.update_log, name='update_log'),

    url(r'^student/all$', views.student_all, name='student_all'),

    url(r'^(?P<exam>\w+)/answer/all$', views.answer_all, name='answer_all'),

    url(r'^$', views.index, name='index'),
)
