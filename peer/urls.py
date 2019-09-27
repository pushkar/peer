from django.urls import include, path
from django.contrib import admin
from student import views
import django.contrib.staticfiles.views as static_views

admin.autodiscover()

urlpatterns = [
    path('', views.index, name='index'),
    path('student/', include('student.urls')),
    path('assignment/', include('assignment.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('static/<slug:path>', static_views.serve),
    # path('exam/', include('exam.urls')),
]
