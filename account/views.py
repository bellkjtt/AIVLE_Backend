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
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from .utils import *


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
            id = data['id']
            email = data['email']
            password = data['password']
            password_confirm = data['password_confirm']
            name = data.get('name', '')

            # 이메일 형식 유효성 검사
            validate_email(email)
            
            # ID 중복 확인
            if Account.objects.filter(id=id).exists():
                return JsonResponse({"message": "EXISTS_ID"}, status=400)

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
                id=id,
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
        

# 로그인 뷰 생성
class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f"JSON decode error: {str(e)}"}, status=400)

        try:
            # 사용자 ID로 로그인
            if Account.objects.filter(id=data["id"]).exists():
                user = Account.objects.get(id=data["id"])

                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    try:
                        # JWT 토큰 생성
                        payload = {'user': str(user.id)}
                        token = jwt.encode(payload, SECRET_KEY['secret'], algorithm=SECRET_KEY['algorithm'])
                        return JsonResponse({"token": token}, status=200)
                    except jwt.PyJWTError as e:
                        return JsonResponse({'message': f"Token generation failed: {str(e)}"}, status=500)

                return JsonResponse({'message': "Invalid password"}, status=401)

            return JsonResponse({'message': "User not found"}, status=400)
        
        except KeyError as e:
            return JsonResponse({'message': f"Missing key: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({'message': f"An unexpected error occurred: {str(e)}"}, status=500)
        
# 이메일로 아이디 찾기 
class FindIDView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        
        mail_title = "아이디 찾기 인증 코드"
        message_template = "인증 코드는 {code} 입니다."
        
        return verify_email(email, mail_title, message_template)


class FindPWView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        
        mail_title = "비밀번호 변경 인증 코드"
        message_template = "인증 코드는 {code} 입니다."
        
        return verify_email(email, mail_title, message_template)
       
# 이메일 인증 코드 확인
class IDVerifyCodeView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        cred_type = 'id'
        
        return verify_code(email, code, cred_type)
    
class PWVerifyCodeView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        cred_type = 'pw'
        
        return verify_code(email, code, cred_type)
    
# 비밀번호 변경
class ChangePWView(View):
    def post(self, request):
        data = json.loads(request.body)
        id = data['id']
        password = data['password']
        password_confirm = data['password_confirm']
        
        return change_pw(id, password, password_confirm)
        