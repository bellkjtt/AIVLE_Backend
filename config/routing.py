# config/routing.py

from django.urls import path
from stt.consumers import STTConsumer


# 웹소켓 URL 패턴을 정의
websocket_urlpatterns = [ 
    path('ws/transcribe/', STTConsumer.as_asgi()),
]
