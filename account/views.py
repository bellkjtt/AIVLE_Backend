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
            name = data.get('name', '')

            # 비밀번호 길이 유효성 검사
            if is_valid_password(password):
                return JsonResponse({"message": "WRONG_FORM"}, status=400)
            
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

            return JsonResponse({"message": "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"message": "INVALID_KEYS"}, status=400)
        except ValidationError:
            return JsonResponse({"message": "INVALID_EMAIL_FORMAT"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

        
# ID 중복 확인
class IDCheck(View):
    def post(self, request):
        data = json.loads(request.body)
        id = data["id"]
        
        if Account.objects.filter(id=id).exists():
            return JsonResponse({"message": "EXISTS_ID"}, status=400)

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

# 회원가입 이메일 인증 코드 전송 
class SignUpMailView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        
        mail_title = "회원가입 인증 코드"
        message_template = "인증 코드는 {code} 입니다."
        
        return verify_email_signup(email, mail_title, message_template)

# 회원가입 이메일 인증 코드 확인
class EMailVerifyCodeView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        cred_type = 'sign'
        
        return verify_code(email, code, cred_type)

       
# ID 찾기 이메일 인증 코드 확인
class IDVerifyCodeView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        cred_type = 'id'
        
        return verify_code(email, code, cred_type)
    
# PW 이메일 인증 코드 확인
class PWVerifyCodeView(View):
    def post(self, request):
        data = json.loads(request.body)
        id = data.get('id')
        email = data.get('email')
        code = data.get('code')
        cred_type = 'pw'
        
        return verify_code(email, code, cred_type, id)
    
# 비밀번호 변경
class ChangePWView(View):
    def post(self, request):
        data = json.loads(request.body)
        id = data['id']
        email = data['email']
        password = data['password']
        password_confirm = data['password_confirm']
        
        return change_pw(id, email, password, password_confirm)
        
        
# JWT 회원정보 전송
@method_decorator(csrf_exempt, name='dispatch')
class JWTuser(View):
    def post(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, SECRET_KEY['secret'], algorithms=SECRET_KEY['algorithm'])
            id = payload.get('user')
            user = Account.objects.get(id=id)
            
            return JsonResponse({"id":user.id, "name":user.name, "email":user.email, "is_admin":user.is_admin}, status=200)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message":"Token_expired"}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({"message":"Invalid token"}, status=400)
        except jwt.DecodeError:
            return JsonResponse({"message":"Decoding_Error"}, status=400)
        except Exception as e:
            return JsonResponse({"message":f"An error occurred: {str(e)}"}, status=400)
            
        
# # 계정 활성화 뷰
# class Activate(View):
#     # GET 요청에 대한 처리 - 계정 활성화 로직
#     def get(self, request, uidb64, token):
#         try:
#             uid  = force_str(urlsafe_base64_decode(uidb64)) # base64로 인코딩된 사용자 ID 디코딩
#             user = Account.objects.get(pk=uid) # 사용자 객체 조회
             
#             # 토큰 유효성 검사
#             if account_activation_token.check_token(user, token):  
#                 user.is_active = True
#                 user.save()
#                 return redirect(EMAIL['REDIRECT_PAGE']) # 이메일 인증 완료 후 리디렉션
        
#             return JsonResponse({"message" : "AUTH FAIL"}, status=400)

#         except ValidationError:
#             return JsonResponse({"message" : "TYPE_ERROR"}, status=400)
#         except KeyError:
#             return JsonResponse({"message" : "INVALID_KEY"}, status=400)