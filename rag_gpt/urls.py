from django.urls import path
from rag_gpt import views

app_name = 'rag_gpt'

urlpatterns = [
    path("ETRI/", views.etri_api, name='etri'),    # ETRI 무료 (긴급 구조 신고 상황 판단)
    path("GPT/", views.gpt_api, name='gpt'),     # GPT 유료 (긴급 구조 신고 상황 판단)
]
