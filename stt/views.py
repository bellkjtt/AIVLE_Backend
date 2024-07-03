from django.shortcuts import render, HttpResponse, redirect, resolve_url
from .models import *
# Create your views here.


# STT API를 활용해 음성 정보 Text 화
def voice_stt(request):

    import urllib3
    import json
    import base64
    
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"        # 음성 인식 API 주소
    apiKey = "d6dec6aa-41bf-48c4-9b3a-acbd97a70b3e"                         # API 키
    language = "korean"                                                     # 언어
    
    audioPath = "t.wav"                                                 # 음성 파일
    
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
    print(data['return_object']['recognized'])
    
    # 복호화된 Text 파일 Return
    # return HttpResponse(data['return_object']['recognized'])

    # 대화 기록 Model에 저장
    chat_log = Chat_log()
    chat_log.message = data['return_object']['recognized']
    chat_log.save()
    
    return redirect(resolve_url('stt:analyze_sentence'))
    
    
    
    
# Text 분석 질의 API를 활용하여 대화에서 필요한 정보 추출 (신고 장소, 인원, 인상착의 .... )
def analyze_sentence(request):
    
    import urllib3
    import json
    
    openApiURL = "http://aiopen.etri.re.kr:8000/MRCServlet"                     # 문장 분석 API 주소
    apiKey = "d6dec6aa-41bf-48c4-9b3a-acbd97a70b3e"                             # API 키
    
    
    # 대화 기록
    chat_log = Chat_log.objects.all()
    talkLog = str(chat_log.last())
    # talkLog = "분당 KT 앞 빽다방에 불났어요"

    # 질의
    question = "불난 장소가 어디에요?"                                          # 장소 추정
    
    
    # 요청 형식 (질의, 대화 기록)
    requestJson = {
        "argument": {
            "question": question,
            "passage": talkLog
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
    
    # GPT 응답 Text 복호화
    data = json.loads(response.data.decode("utf-8", errors='ignore'))

    # GPT 응답 Text Return
    return HttpResponse(data['return_object']['MRCInfo']['answer']) 