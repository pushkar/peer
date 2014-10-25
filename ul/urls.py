from django.conf.urls import patterns, url

from ul import views

urlpatterns = patterns('',
    url(r'^exam$', views.exam, name='exam'),
    url(r'^done$', views.done, name='done'),
    url(r'^save$', views.save, name='save'),
    url(r'^update/(?P<q_id>[0-9]+)$', views.update, name='update'),

    url(r'^exam/tf$', views.exam_tf, name='exam_tf'),
    url(r'^exam/mc$', views.exam_mc, name='exam_mc'),
    url(r'^exam/essay$', views.exam_essay, name='exam_essay'),
    url(r'^db/populate$', views.db_populate, name='db_populate'),
    url(r'^db/show$', views.db_show, name='db_show'),
    url(r'^$', views.index, name='index'),
)
