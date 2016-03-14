from django.conf.urls import url

from codework import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^grade$', views.grade, name='grade'),
    url(r'^(?P<a_name>\w+)/$', views.work, name='work'),
    url(r'^import/(?P<a_name>\w+)/$', views.import_pairs, name='import_pairs'),
    url(r'^update/(?P<id>[0-9]+)/$', views.update, name='update'),
    url(r'^hw4/csv/$', views.hw4_csv, name='hw4_csv'),
]
