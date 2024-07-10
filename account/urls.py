from django.urls import path
from .views      import SignUpView, Activate

urlpatterns = [
    path('signup/', SignUpView.as_view()), # 회원가입 api
    path('activate/<str:uidb64>/<str:token>/', Activate.as_view()), # 메일 인증 api
]