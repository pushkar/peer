from django.conf.urls import url

from assignment import views

app_name = "assignment"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<a_name>\w+)/$', views.home, name='home'),
    url(r'^(?P<a_name>\w+)/(?P<p_name>\w+)/$', views.page, name='page'),
    url(r'^(?P<a_name>\w+)/admin/admin/$', views.admin, name='admin'),
    url(r'^(?P<a_name>\w+)/admin/csv/$', views.download_as_csv, name='download_as_csv'),
    url(r'^(?P<a_name>\w+)/code$', views.code, name='code'),
    url(r'^code/update/(?P<id>[0-9]+)/$', views.update, name='update'),
]
