from django.conf.urls import patterns, url

from exam import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<exam_name>\w+)$', views.get_or_create_exam, name='get_or_create_exam'),
    url(r'^(?P<exam_name>\w+)/save$', views.save_exam, name='save_exam'),
    url(r'^(?P<exam_name>\w+)/submit$', views.submit_exam, name='submit_exam'),

)
