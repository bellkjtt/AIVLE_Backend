# account/utils.py

import random
import string
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.http import JsonResponse
from .models import Account
import bcrypt

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

# 이메일 코드 인증
def verify_code(email, code, cred_type):
    if not email or not code:
        return JsonResponse({"message":"EMAIL_OR_CODE_REQUIRED"}, status=400)
    
    cached_code = cache.get(f'verify_code_{email}')
    
    if cached_code and cached_code == code:
        try:
            user = Account.objects.get(email=email)
            if cred_type == 'id':
                return JsonResponse({"message": "SUCCESS", "id": user.id}, status=200)
            elif cred_type == 'pw':
                return JsonResponse({"message": "SUCCESS"}, status=200)
        except Account.DoesNotExist:
            return JsonResponse({"message": "EMAIL_NOT_FOUND"}, status=404)
    else:
        return JsonResponse({"message": "INVALID_CODE"}, status=400)
    
# 비밀번호 변경
def change_pw(id, pw, pw_conf):
    if Account.objects.filter(id=id).exists():
        user = Account.objects.get(id=id)

    if pw != pw_conf:
        return JsonResponse({"message":"PASSWORD_MISMATCH"}, status=400)
    
    # 비밀번호 암호화
    user.password=bcrypt.hashpw(pw.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")
    user.save()
    
    return JsonResponse({"message":"PASSWORD_CHANGED"}, status = 200)