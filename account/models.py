from django.db import models


# 회원 정보 모델
class Account(models.Model):
    name       = models.CharField(max_length=50)
    email      = models.EmailField(max_length=254, unique=True)
    password   = models.CharField(max_length=200)
    is_admin   = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts'
