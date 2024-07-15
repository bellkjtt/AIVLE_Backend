from django.urls import path
from .views import StartRecordingAPIView, StopRecordingAPIView, index

urlpatterns = [
    path('', index, name='index'),
    path('start_recording/', StartRecordingAPIView.as_view(), name='start_recording'),
    path('stop_recording/', StopRecordingAPIView.as_view(), name='stop_recording'),
]
