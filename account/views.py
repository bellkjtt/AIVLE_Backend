from django.views import View
from django.http import JsonResponse, HttpResponse
import json, jwt
import bcrypt
from .models import Account
import re
from config.token     import account_activation_token
from config.text      import message
from config.settings  import SECRET_KEY
from config.smtp_settings import EMAIL
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts  import redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding           import force_bytes, force_str

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

# 회원가입 뷰 생성
class SignUpView(View):
    # GET 요청에 대한 처리 - CSRF 쿠키 설정
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return JsonResponse({"message": "CSRF cookie set"}, status=200)
    
    # POST 요청 시 회원가입
    def post(self, request):
        data = json.loads(request.body)

        try:
            email = data['email']
            password = data['password']
            password_confirm = data['password_confirm']
            name = data.get('name', '')

            # 이메일 형식 유효성 검사
            validate_email(email)

            # 비밀번호 길이 유효성 검사
            if len(password) < 8:
                return JsonResponse({"message": "PASSWORD_TOO_SHORT"}, status=400)

            # 비밀번호 재확인 검사
            if password != password_confirm:
                return JsonResponse({"message": "PASSWORD_MISMATCH"}, status=400)

            # 이메일 중복 확인
            if Account.objects.filter(email=email).exists():
                return JsonResponse({"message": "EXISTS_EMAIL"}, status=400)

            # 계정 생성
            user = Account.objects.create(
                name=name,
                email=email,
                password=bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                is_admin=False,  # 기본값으로 설정
                is_active=False  # 이메일 인증 전까지 비활성화 상태
            )

            # 이메일 인증 메일 발송
            current_site = get_current_site(request)                # 요청을 통해 현재 사이트 정보 가져오기
            domain = current_site.domain                            # 도메인 정보 추출
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))    # 사용자 ID를 base64로 인코딩
            token = account_activation_token.make_token(user)       # 사용자에 대한 토큰 생성
            message_data = message(domain, uidb64, token)           # 메세지 생성

            mail_title = "이메일 인증을 완료해주세요"
            mail_to = email
            email_message = EmailMessage(mail_title, message_data, to=[mail_to])
            email_message.send()

            return JsonResponse({"message": "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"message": "INVALID_KEYS"}, status=400)
        except ValidationError:
            return JsonResponse({"message": "INVALID_EMAIL_FORMAT"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 계정 활성화 뷰
class Activate(View):
    # GET 요청에 대한 처리 - 계정 활성화 로직
    def get(self, request, uidb64, token):
        try:
            uid  = force_str(urlsafe_base64_decode(uidb64)) # base64로 인코딩된 사용자 ID 디코딩
            user = Account.objects.get(pk=uid) # 사용자 객체 조회
             
            # 토큰 유효성 검사
            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()

                return redirect(EMAIL['REDIRECT_PAGE']) # 이메일 인증 완료 후 리디렉션
        
            return JsonResponse({"message" : "AUTH FAIL"}, status=400)

        except ValidationError:
            return JsonResponse({"message" : "TYPE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({"message" : "INVALID_KEY"}, status=400)