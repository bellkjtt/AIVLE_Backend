# stt/views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64, urllib3, json


# CSRF 보호 비활성화
@csrf_exempt
def speech_to_text(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        audio_contents = base64.b64encode(audio_file.read()).decode("utf8")
        
        openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
        apiKey = "api_key"
        language = "korean"
        
        requestJson = {
            "argument": {
                "language_code": language,
                "audio": audio_contents
            }
        }
        
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8","Authorization": apiKey},
            body=json.dumps(requestJson)
        )
        
        if response.status == 200:
            data = json.loads(response.data.decode("utf-8", errors='ignore'))
            recognized_text = data['return_object']['recognized']
            return JsonResponse({"recognized_text": recognized_text}, status=200)
        else:
            return JsonResponse({"error": "API request failed"}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)

from rest_framework import viewsets, mixins, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, HttpResponse, redirect, resolve_url
from .models import *

import urllib3
import json
import base64

class ChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_log
        fields = '__all__'

# STT API를 활용해 음성 정보 Text 화    
# STT routing을 위한 view 함수 viewsets화
class STTViewSet(viewsets.ModelViewSet):

    serializer_class = ChatLogSerializer
    queryset = Chat_log.objects.all()

    
    # ViewSet 클래스 내에서 사용자가 정의한 액션을 정함
    # detail=False : URL에 객체 ID 포함 X, post 형식
    @action(detail=False, methods=['post'])
    def voice_stt(self, request):
        80000
        openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"        # 음성 인식 API 주소
        apiKey = "d6dec6aa-41bf-48c4-9b3a-acbd97a70b3e"                         # API 키
        language = "korean" # 언어
        
        # 음성 파일
        audioPath = "STT.wav"     
             
        # 음성 파일 압축 (인코딩)
        file = open(audioPath, "rb")
        audioContents = base64.b64encode(file.read()).decode("utf8")
        file.close()
        
        # 요청 형식 (언어, 음성)
        requestJson = {    
            "argument": {
                "language_code": language,
                "audio": audioContents
            }
        }
        
        # HttpRequest 요청 (응답)
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8","Authorization": apiKey},
            body=json.dumps(requestJson)
        )
        
        # 응답 코드 확인
        print("[responseCode] " + str(response.status))
        print("[responBody]")
        print(str(response.data,"utf-8"))
        
        # Text 파일 복호화
        data = json.loads(response.data.decode("utf-8", errors='ignore'))
        #복화화된 Text 파일
        data_text = data['return_object']['recognized']
        print(data_text)
        
        # # 대화 기록 Model에 저장
        chat_log = Chat_log(message=data_text)
        chat_log.save()
        
        # 복호화된 Text 파일 Return
        # rest_framework을 통한 resopnse
        return Response(data_text)
        
        
    


    
    
