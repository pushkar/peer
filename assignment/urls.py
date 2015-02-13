from django.conf.urls import patterns, url

from assignment import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<a_name>\w+)/$', views.home, name='home'),
    url(r'^(?P<a_name>\w+)/(?P<p_name>\w+)/$', views.page, name='page'),
    url(r'^(?P<a_name>\w+)/page/stats/$', views.stats, name='stats'),
    url(r'^(?P<a_name>\w+)/submission$', views.submission, name='submission'),
    url(r'^(?P<a_name>\w+)/review/(?P<id>[0-9]+)$', views.review, name='review'),

    url(r'^(?P<a_name>\w+)/reviewconvo/(?P<id>[0-9]+)$', views.submit_reviewconvo, name='submit_reviewconvo'),
    url(r'^(?P<a_name>\w+)/reviewscore/(?P<review_id>[0-9]+)/(?P<value>[0-9]+)$', views.submit_reviewscore, name='submit_reviewscore'),
)
