# config/smtp_settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # DB 엔진 SQLite 사용
        'NAME': 'DB.sqlite3',                   # DB 이름
    }
}

#  JWT 시크릿 키 설정
SECRET_KEY = {
    'secret': 'm!#@+v40p*05jd2fds2fe)me1f&4mvfi!igbv7b^2dyrn5=o2dw!i-0u7*&^',  # 비밀 키
    'algorithm': 'HS256'  # 알고리즘 (여기서는 HS256 사용)
}

# SMTP 설정
EMAIL = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',  # SMTP 이메일 백엔드
    'EMAIL_USE_TLS': True,       # TLS 사용 여부 (보안용)
    'EMAIL_PORT': 587,           # SMTP 포트
    'EMAIL_HOST': 'smtp.naver.com',  # Naver SMTP 사용
    'EMAIL_HOST_USER': 'ysy6700',  # Naver 이메일 계정
    'EMAIL_HOST_PASSWORD': 'aivle202405!',  # Naver 이메일 계정 비밀번호
    'DEFAULT_FROM_EMAIL': 'ysy6700@naver.com',  # 기본 발신 이메일 주소
    'SERVER_EMAIL': 'ysy6700',  # 서버 이메일 주소
    'REDIRECT_PAGE': 'https://auth.edu.kt.co.kr/'  # 이메일 인증 후 리디렉션할 페이지 URL
}
