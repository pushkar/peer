from django.conf.urls import url

from codework import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<a_name>\w+)/$', views.work, name='work'),
]
