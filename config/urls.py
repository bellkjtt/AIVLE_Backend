# config/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stt.views import STTViewSet

# 기본 라우터 객체 생성
router = DefaultRouter()
# STTviewset 뷰셋을 등록
router.register(r'stt', STTViewSet, basename='stt')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
