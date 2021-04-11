
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url
from firstdj import views
from .views import get_data

urlpatterns = [
    path('admin/', admin.site.urls),          
    path('', views.index, name='home'),
    url(r'api/data/$',get_data,name='api-data')
]
