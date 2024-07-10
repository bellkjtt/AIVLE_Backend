from django.views import View
from django.http import JsonResponse, HttpResponse
import json
import bcrypt
from .models import Account
import re

class SignUp(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            email = data['email']
            password = data['password']
            password_confirm = data['password_confirm']
            name = data.get('name', '')

            # 이메일 형식 유효성 검사
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return JsonResponse({"message": "INVALID_EMAIL_FORMAT"}, status=400)

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
            Account.objects.create(
                name=name,
                email=email,
                password=bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                is_admin=False  # 기본값으로 설정
            ).save()

            return JsonResponse({"message": "SUCCESS"}, status=200)
            
        except KeyError:
            return JsonResponse({"message": "INVALID_KEYS"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
