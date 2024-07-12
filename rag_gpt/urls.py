from django.urls import path
from rag_gpt import views

app_name = 'rag_gpt'

urlpatterns = [
    path("", views.analyze_sentence, name='analyze_sentence'),    # 문장 분석 (긴급 구조 신고 상황 판단)
]
