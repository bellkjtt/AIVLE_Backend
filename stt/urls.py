from django.urls import path
from stt import views

app_name = 'stt'

urlpatterns = [
    path("voice_stt/", views.voice_stt, name='voice_stt'),                         # STT 음성 인식
    path("analyze_sentence/", views.analyze_sentence, name='analyze_sentence'),    # 문장 분석 (장소 추정)
]
