# config/urls.py

from django.contrib import admin
from django.urls import path, include
from stt import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    # stt view 연결
    path('speech_to_text/', views.speech_to_text, name='speech_to_text'), 
    path('account/', include('account.urls'))
]
