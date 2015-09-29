from django.conf.urls import patterns, url

from student import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^messages$', views.messages_all, name='messages_all'),
    url(r'^optin$', views.optin, name='optin'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^updates$', views.updates, name='updates'),

    url(r'^admin$', views.admin, name='admin'),
    url(r'^admin/reviews$', views.admin_review_assignments, name='admin_review_assignments'),

    url(r'^pass$', views.pass_request, name='pass_request'),
    url(r'^populate$', views.populate, name='populate'),

    url(r'^group/(?P<group_id>\d+)$', views.group, name='group'),
    url(r'^login/(?P<user>\w+)$', views.login_change, name='login_change'),
)
