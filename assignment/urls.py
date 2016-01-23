from django.conf.urls import url

from assignment import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<a_name>\w+)/$', views.home, name='home'),
    url(r'^(?P<a_name>\w+)/(?P<p_name>\w+)/$', views.page, name='page'),
    url(r'^(?P<a_name>\w+)/page/stats/$', views.stats, name='stats'),
    url(r'^(?P<a_name>\w+)/page/admin/reviews/(?P<action>\w+)/(?P<order_by>\w+)$', views.admin_reviews, name='admin_reviews'),
    url(r'^(?P<a_name>\w+)/page/admin/stats$', views.admin_stats, name='admin_stats'),
    url(r'^(?P<a_name>\w+)/page/admin$', views.admin, name='admin'),

    url(r'^(?P<a_name>\w+)/page/rdebug/$', views.review_debug, name='rdebug'),

    url(r'^(?P<a_name>\w+)/submission$', views.submission, name='submission'),
    url(r'^(?P<a_name>\w+)/submission/(?P<username>\w+)/files$', views.submission_files, name='submission_files'),
    url(r'^(?P<a_name>\w+)/submission/add$', views.submission_add, name='submission_add'),
    url(r'^(?P<a_name>\w+)/submission/(?P<id>[0-9]+)/delete$', views.submission_delete, name='submission_delete'),

    url(r'^(?P<a_name>\w+)/(?P<submission_id>[0-9]+)/find_reviewers$', views.find_reviewers, name='find_reviewers'),
    url(r'^(?P<a_name>\w+)/(?P<submission_id>[0-9]+)/find_reviews$', views.find_reviews, name='find_reviews'),

    url(r'^(?P<a_name>\w+)/review/(?P<id>[0-9]+)$', views.review, name='review'),
    url(r'^(?P<a_name>\w+)/reviewconvo/(?P<id>[0-9]+)$', views.review_convo, name='review_convo'),
    url(r'^(?P<a_name>\w+)/reviewconvo_addlike/(?P<review_id>[0-9]+)$', views.reviewconvo_addlike, name='reviewconvo_addlike'),
    url(r'^(?P<a_name>\w+)/reviewconvo_removelike/(?P<review_id>[0-9]+)$', views.reviewconvo_removelike, name='reviewconvo_removelike'),
    url(r'^(?P<a_name>\w+)/reviewmenu/1$', views.review_menu, name='review_menu'),


    url(r'^(?P<a_name>\w+)/reviewconvosubmit/(?P<id>[0-9]+)$', views.submit_reviewconvo, name='submit_reviewconvo'),
    url(r'^(?P<a_name>\w+)/reviewconvodelete/(?P<id>[0-9]+)$', views.delete_reviewconvo, name='delete_reviewconvo'),

    url(r'^(?P<a_name>\w+)/reviewscore/(?P<review_id>[0-9]+)/(?P<value>[0-9]+)$', views.submit_reviewscore, name='submit_reviewscore'),
    url(r'^(?P<a_name>\w+)/addreviewscore/(?P<review_id>-?[0-9]+)/(?P<value>[+,-]?[0-9]+)$', views.submit_add_reviewscore, name='submit_add_reviewscore'),
]
