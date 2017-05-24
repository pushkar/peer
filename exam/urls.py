from django.conf.urls import url

from exam import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<exam_name>\w+)$', views.get_or_create_exam, name='get_or_create_exam'),
    url(r'^(?P<exam_name>\w+)/save$', views.save_exam, name='save_exam'),
    url(r'^(?P<exam_name>\w+)/submit$', views.submit_exam, name='submit_exam'),
    url(r'^(?P<exam_name>\w+)/admin$', views.admin_exam, name='admin_exam'),
    url(r'^graders/(?P<id>\d+)$', views.graders, name='graders'),
]
