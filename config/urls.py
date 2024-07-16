# config/urls.py

from django.contrib import admin
from django.urls import path, include
from stt import views  

urlpatterns = [
    path('admin/', admin.site.urls),                   # 관리자
    path('', include('stt.urls')),
    path('rag_gpt/', include('rag_gpt.urls')),         # RAG_GPT (긴급 구조 신고 상황 판단)
    path('account/', include('account.urls')),         # 회원정보
    path('api/', include("api.urls")),                 # 모델링
    path('post/', include("post.urls")),               # 게시판
]
