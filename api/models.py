from django.db import models

class Result(models.Model):
    address = models.CharField(max_length=100)
    disaster_large = models.CharField(max_length=10)
    disaster_medium = models.CharField(max_length=10)
    urgency_level = models.CharField(max_length=10)
    sentiment = models.CharField(max_length=10)
    symptom = models.CharField(max_length=100, null=True)
    triage = models.CharField(max_length=100, null=True)
    text = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.address
