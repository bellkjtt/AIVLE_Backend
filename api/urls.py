# api/urls.py
from django.urls import path
#from .views import PredictView, Disaster
from .views import Disaster

urlpatterns = [
    #path('predict/', PredictView.as_view(), name='predict'),
    path('disaster-data/', Disaster.as_view(), name='disaster'),
    
]