from functools import wraps
from django.http import JsonResponse
import jwt
from account.models import Account
from .settings import SECRET_KEY  # SECRET_KEY는 설정 파일에서 가져와야 합니다.

def verify_jwt_token(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({"message": "Authorization header missing"}, status=400)
            
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            payload = jwt.decode(token, SECRET_KEY['secret'], algorithms=[SECRET_KEY['algorithm']])
            user_id = payload.get('user')

            # 사용자 객체를 가져옴
            user = Account.objects.get(id=user_id)
            request.user = user  # 사용자 객체를 request에 추가
            return view_func(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token expired"}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=400)
        except jwt.DecodeError:
            return JsonResponse({"message": "Decoding error"}, status=400)
        except Account.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=400)
    
    return wrapped_view
