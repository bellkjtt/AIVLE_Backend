from django.db import models

# Create your models here.

# 긴급 구조 신고 전화기록
class EmergencyCalls(models.Model):
    
    date = models.DateTimeField(auto_now_add=True, verbose_name="신고 날짜")
    category = models.CharField(max_length=255, verbose_name="사건 분류")
    location = models.CharField(max_length=255, verbose_name="사건 발생 장소")
    details = models.TextField(verbose_name="구체적인 현장 상태", null=True)
    address_name = models.CharField(max_length=255, verbose_name="추정 주소", null=True)
    place_name = models.CharField(max_length=255, verbose_name="추정 장소", null=True)
    phone_number = models.CharField(max_length=20, verbose_name="전화번호", null=True)
    
    def __str__(self):
        return f"{self.date} - {self.category} at {self.location}"

    class Meta:
        ordering = ['-date']