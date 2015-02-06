from django.conf.urls import patterns, url

from assignment import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<a_name>\w+)/$', views.assignment_view, name='assignment_view'),
    url(r'^(?P<a_name>\w+)/(?P<p_name>\w+)/$', views.assignment_page, name='assignment_page'),
    url(r'^(?P<a_name>\w+)/report$', views.submit_report, name='submit_report'),
    url(r'^(?P<a_name>\w+)/review$', views.submit_review, name='submit_review'),
    url(r'^(?P<a_name>\w+)/review/(?P<review_pk>[0-9]+)$', views.submit_reviewtext, name='submit_reviewtext'),
    url(r'^(?P<a_name>\w+)/reviewscore/(?P<review_pk>[0-9]+)$', views.submit_reviewscore, name='submit_reviewscore'),

    url(r'^(?P<a_name>\w+)/adminview$', views.adminview, name='adminview'),
)
