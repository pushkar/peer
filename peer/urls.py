from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'mcscheme.views.index', name='index'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^mcscheme/', include('mcscheme.urls', namespace="mcscheme")),
	url(r'^accounts/login/', include(admin.site.urls)),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
