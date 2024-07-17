# config/urls.py

from django.contrib import admin
from django.urls import path, include
from stt import views  

urlpatterns = [
    path('admin/', admin.site.urls),                   # 관리자
    path('', include('stt.urls')),

    
    # stt view 연결
    path('account/', include('account.urls')),
    path('api/', include("api.urls")),
    
]

