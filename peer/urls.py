from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'student.views.index', name='index'),
    url(r'^student/', include('student.urls', namespace="student")),
	url(r'^sl/', include('sl.urls', namespace="sl")),
    url(r'^ul/', include('ul.urls', namespace="ul")),
    url(r'^rl/', include('rl.urls', namespace="rl")),
    url(r'^recommender/', include('recommender.urls', namespace="recommender")),
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^grade/', include('grade.urls', namespace="grade")),
	url(r'^accounts/login/', include(admin.site.urls)),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
