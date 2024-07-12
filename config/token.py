# config/token.py

# 계정 활성화 토큰 생성 -> 사용자 이메일로 계정 활성화

import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# 계정 활성화 커스텀 토큰 생성
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    # 해시 값 생성 메서드
    def _make_hash_value(self, user, timestamp):
        # 사용자 ID, 타임스탬프, 활성화 상태를 문자열로 변환하고 연결하여 해시 값을 생성
        return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(user.is_active)
        
# 계정 활성화 토큰 생성 인스턴스
account_activation_token = AccountActivationTokenGenerator()
