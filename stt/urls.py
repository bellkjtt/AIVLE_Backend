from django.urls import path
from .views import ProcessAudioView
from . import views

urlpatterns = [
    path('process_audio/', ProcessAudioView.as_view(), name='process_audio'),
]
