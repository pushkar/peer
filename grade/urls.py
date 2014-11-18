from django.conf.urls import patterns, url

from grade import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<exam>\w+)$', views.grade_exam, name='grade_exam'),
    url(r'^(?P<exam>\w+)/q/(?P<q_id>\w+)$', views.grade_question, name='grade_question'),

    url(r'^q/all$', views.questions_all, name='questions_all'),
    url(r'^q/(?P<q_id>\d+)$', views.question, name='question'),
    url(r'^update/tflog/id/(?P<id>\d+)/score/(?P<score>\d+.\d+)$', views.tflog_update, name='tflog_update'),
    url(r'^update/mclog/id/(?P<id>\d+)/score/(?P<score>\d+.\d+)$', views.mclog_update, name='mclog_update'),
)
