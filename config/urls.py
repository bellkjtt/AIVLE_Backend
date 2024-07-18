# config/urls.py

from django.contrib import admin
from django.urls import path, include
from stt import views  

urlpatterns = [
    path('admin/', admin.site.urls),                   # 관리자
    path('', include('stt.urls')),
    path('account/', include('account.urls')),
    path('api/', include("api.urls")),
    path('post/', include('post.urls')),
]

