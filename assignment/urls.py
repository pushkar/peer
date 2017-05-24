from django.conf.urls import url

from assignment import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<a_name>\w+)/$', views.home, name='home'),
    url(r'^(?P<a_name>\w+)/(?P<p_name>\w+)/$', views.page, name='page'),
    url(r'^(?P<a_name>\w+)/code$', views.code, name='code'),
    url(r'^code/update/(?P<id>[0-9]+)/$', views.update, name='update'),
]
