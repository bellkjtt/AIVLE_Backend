from django.db import models

# Create your models here.

# 대화 기록 Model
class Chat_log(models.Model):
    
    # 필드
    timestamp = models.DateTimeField(auto_now_add=True)  # 대화가 기록된 시간을 자동으로 설정
    message = models.TextField()  # 대화 내용을 저장

    # 객체 출력 문자열
    def __str__(self):
        return f'{self.timestamp} - {self.message[:50]}...' 

    # 시간 내림차순으로 정렬
    class Meta:
        ordering = ['-timestamp']  