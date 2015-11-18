from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'student.views.index', name='index'),
    url(r'^student/', include('student.urls', namespace="student")),
    url(r'^assignment/', include('assignment.urls', namespace="assignment")),
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^record/', include('record.urls', namespace="record")),
    #url(r'^exam/', include('exam.urls', namespace="exam")),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
