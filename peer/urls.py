from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'sl.views.index', name='index'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^sl/', include('sl.urls', namespace="sl")),
    url(r'^ul/', include('ul.urls', namespace="ul")),
    url(r'^api/', include('api.urls', namespace="api")),
	url(r'^accounts/login/', include(admin.site.urls)),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
