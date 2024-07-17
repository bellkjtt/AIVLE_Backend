# api/urls.py
from django.urls import path
from .views import Disaster,PredictView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('disaster-data/', Disaster.as_view(), name='disaster'),
]