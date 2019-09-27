from django.conf.urls import url

from student import views

app_name = "student"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^messages$', views.messages_all, name='messages_all'),
    url(r'^optin$', views.optin, name='optin'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^about$', views.about, name='about'),

    url(r'^admin$', views.admin, name='admin'),
    url(r'^pass$', views.pass_request, name='pass_request'),

    url(r'^login/(?P<user>\w+)$', views.login_change, name='login_change'),
]
