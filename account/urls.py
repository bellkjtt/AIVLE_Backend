from django.urls import path
from .views      import *

urlpatterns = [
    path('signup/', SignUpView.as_view()), # 회원가입 api
    path('activate/<str:uidb64>/<str:token>/', Activate.as_view()), # 메일 인증 api
    path('signin/', SignInView.as_view()), # 로그인
    path('findid/', FindIDView.as_view()), # 아이디 찾기
    path('findpw/', FindPWView.as_view()), # 비밀번호 찾기
    path('verifyid/', IDVerifyCodeView.as_view()), # 이메일 코드 확인
    path('verifypw/', PWVerifyCodeView.as_view()), # 이메일 코드 확인
    path('changepw/', ChangePWView.as_view()), # 이메일 코드 확인
]