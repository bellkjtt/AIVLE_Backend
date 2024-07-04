import os
from django.core.asgi import get_asgi_application

# 환경변수 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Django ASGI app 초기화
django_asgi_app = get_asgi_application()

# channels 라우팅과 미들웨어는 Django 초기화 이후 가져와야 한다고 함.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from .routing import websocket_urlpatterns

application = ProtocolTypeRouter({      # 들어오는 연결을 프로토콜 유형에 따라 처리 ProtocolTypeRouter
    "http": django_asgi_app,            # 장고 ASGI app으로 보내 일반적인 http 처리
    "websocket":                        # 웹소켓 처리 
        AuthMiddlewareStack(            # Django의 인증 시스템을 웹소켓에 적용
            AllowedHostsOriginValidator(# ALLOWED_HOSTS 설정을 사용 웹소켓 출처 검증 -> 허용된 호스트만 사용가능
            URLRouter(                  # URL 패턴에 따라 웹소켓 요청 라우팅
                websocket_urlpatterns
            )     
        ),
    ),
})

## 웹소켓 통신을 안전하고 효율적으로 처리 가능