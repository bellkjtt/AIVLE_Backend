from django.db import models

# 공지 사항 모델
class Post(models.Model):
    id         = models.AutoField(primary_key=True)
    user_id    = models.CharField(max_length=16)
    title      = models.CharField(max_length=50)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    file       = models.FileField(null=True, upload_to="", blank=True)

    class Meta:
        db_table = 'post'
        
    def __str__(self):
            return self.title