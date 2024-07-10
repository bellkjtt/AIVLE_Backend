from django.db import models

class Account(models.Model):
    name       = models.CharField(max_length=50)
    email      = models.EmailField(max_length=254, unique=True)
    password   = models.CharField(max_length=200)
    is_admin   = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts'
