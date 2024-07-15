# config/urls.py

from django.contrib import admin
from django.urls import path, include
from stt import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stt/', include('stt.urls')),
    path('rag_gpt/', include('rag_gpt.urls')),         # RAG_GPT (긴급 구조 신고 상황 판단)
    # stt view 연결
    path('speech_to_text/', views.speech_to_text, name='speech_to_text'), 
    path('account/', include('account.urls')),
    path('api/', include("api.urls")),
]
