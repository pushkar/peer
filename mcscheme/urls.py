from django.conf.urls import patterns, url

from mcscheme import views

urlpatterns = patterns('',
    url(r'^home$', views.home, name='home'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^exam$', views.exam, name='exam'),
    url(r'^done$', views.done, name='done'),
    url(r'^save$', views.save, name='save'),
    url(r'^update/(?P<q_id>[0-9]+)$', views.update, name='update'),
    url(r'^exam/tf$', views.exam_tf, name='exam_tf'),
    url(r'^exam/mc$', views.exam_mc, name='exam_mc'),
    url(r'^grade/(?P<log_type>\w+)/(?P<log_id>\d+)/(?P<score>\d+.\d+)$', views.grade, name='grade'),
    url(r'^grade/all$', views.grade_all, name='grade_all'),
    url(r'^grade/auto$', views.grade_auto, name='grade_auto'),
    url(r'^grade/(?P<log_type>\w+)/(?P<log_id>\d+)$', views.grade_log, name='grade_log'),
    url(r'^grade/student/(?P<u_id>\w+)$', views.grade_student, name='grade_student'),
    url(r'^db/populate$', views.db_populate, name='db_populate'),
    url(r'^db/show$', views.db_show, name='db_show'),
    url(r'^$', views.index, name='index'),
)
