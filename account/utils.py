# account/utils.py

import random
import string
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.http import JsonResponse
from .models import Account
import bcrypt, jwt
import re

# 비밀번호 양식 추가
def is_valid_password(password):
    if len(password) < 8:
        return True
    if not re.search(r"[A-Z]", password):
        return True
    if not re.search(r"[0-9]", password):
        return True
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return True
    return False

# 이메일 인증
def verify_email(email, mail_title, message_template):
    if not email:
        return JsonResponse({"valid": False}, status=400)

    try:
        # 이메일 형식 유효성 검사
        validate_email(email)
    except ValidationError:
        return JsonResponse({"valid": False}, status=400)

    try:
        user = Account.objects.get(email=email)

        # 랜덤 인증 코드 생성
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # 캐시에 인증 코드 저장 5분간 유효 (이메일 별)
        cache.set(f'verify_code_{email}', code, 300)

        # 이메일 발송
        message_data = message_template.format(code=code)
        email_message = EmailMessage(mail_title, message_data, to=[email])
        email_message.send()

        return JsonResponse({"valid": True}, status=200)

    except Account.DoesNotExist:
        return JsonResponse({"message": "EMAIL_NOT_FOUND"}, status=404)

# 이메일 인증
def verify_email_signup(email, mail_title, message_template):
    if not email:
        return JsonResponse({"valid": False}, status=400)

    try:
        # 이메일 형식 유효성 검사
        validate_email(email)
    except ValidationError:
        return JsonResponse({"valid": False}, status=400)


    # 랜덤 인증 코드 생성
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # 캐시에 인증 코드 저장 5분간 유효 (이메일 별)
    cache.set(f'verify_code_{email}', code, 300)

    # 이메일 발송
    message_data = message_template.format(code=code)
    email_message = EmailMessage(mail_title, message_data, to=[email])
    email_message.send()

    return JsonResponse({"valid": True}, status=200)


# 이메일 코드 인증
def verify_code(email, code, cred_type, id='11'):
    if not email or not code:
        return JsonResponse({"message":"EMAIL_OR_CODE_REQUIRED"}, status=400)
    
    cached_code = cache.get(f'verify_code_{email}')
    
    if cached_code and cached_code == code:
        if cred_type == 'sign':
            return JsonResponse({"message": "SUCCESS"}, status=200)
        else:
            try:
                user = Account.objects.get(email=email)
                if cred_type == 'id':
                    return JsonResponse({"message": "SUCCESS", "id": user.id}, status=200)
                elif cred_type == 'pw':
                    try:
                        account = Account.objects.get(id=id, email=email) # 아이디와 이메일 매칭
                        return JsonResponse({"message": "SUCCESS"}, status=200)
                    except Account.DoesNotExist:
                        return JsonResponse({"valid": False}, status=400)

            except Account.DoesNotExist:
                return JsonResponse({"message": "EMAIL_NOT_FOUND"}, status=404)
    else:
        return JsonResponse({"message": "INVALID_CODE"}, status=400)
    
# 비밀번호 변경
def change_pw(id, email, pw, pw_conf):
    try:
        user = Account.objects.get(id=id, email=email) # 아이디와 이메일 매칭
        
    except Account.DoesNotExist:
        return JsonResponse({"valid": False}, status=400)
    
    if pw != pw_conf:
        return JsonResponse({"message":"PASSWORD_MISMATCH"}, status=400)
    
    if is_valid_password(pw):
        return JsonResponse({"message": "WRONG_FORM"}, status=400)
    
    # 비밀번호 암호화
    user.password=bcrypt.hashpw(pw.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
    user.save()
    
    return JsonResponse({"message":"PASSWORD_CHANGED"}, status = 200)


from config.settings  import SECRET_KEY


# JWT 검증
def verify_jwt_token(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({"message": "Authorization header missing"}, status=400), None
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        payload = jwt.decode(token, SECRET_KEY['secret'], algorithms=[SECRET_KEY['algorithm']])
        user_id = payload.get('user')

        # 사용자 객체를 가져옴
        user = Account.objects.get(id=user_id)
        return None, user
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Token expired"}, status=400), None
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Invalid token"}, status=400), None
    except jwt.DecodeError:
        return JsonResponse({"message": "Decoding error"}, status=400), None
    except Account.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=404), None
    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=400), None




# 이메일 인증 링크
# current_site = get_current_site(request)                # 요청을 통해 현재 사이트 정보 가져오기
# domain = current_site.domain                            # 도메인 정보 추출
# uidb64 = urlsafe_base64_encode(force_bytes(user.pk))    # 사용자 ID를 base64로 인코딩
# token = account_activation_token.make_token(user)       # 사용자에 대한 토큰 생성
# message_data = message(domain, uidb64, token)           # 메세지 생성

# mail_title = "이메일 인증을 완료해주세요"
# mail_to = email
# email_message = EmailMessage(mail_title, message_data, to=[mail_to])
# email_message.send()

