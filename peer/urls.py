from django.conf.urls import url, include
from django.contrib import admin
from student import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^student/', include('student.urls', namespace="student")),
    url(r'^assignment/', include('assignment.urls', namespace="assignment")),
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^record/', include('record.urls', namespace="record")),
    url(r'^code/', include('codework.urls', namespace="codework")),
    url(r'^exam/', include('exam.urls', namespace="exam")),
    url(r'^admin/', include(admin.site.urls)),
]
