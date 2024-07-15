from django.shortcuts import render, HttpResponse
from .models import *

import requests
from django.conf import settings
from django.http import JsonResponse

# Create your views here.

#######################################  ETRI  #########################################################

# Text 분석 질의 API를 활용하여 대화에서 필요한 정보 추출 (신고 장소, 인원, 인상착의 .... )
def etri_api(request):
    
    import urllib3
    import json
    
    openApiURL = "http://aiopen.etri.re.kr:8000/MRCServlet"                     # 문장 분석 API 주소
    apiKey = "d6dec6aa-41bf-48c4-9b3a-acbd97a70b3e"                             # API 키
    
    
    # 대화 기록
    talkLog = '''
                장소 : KT 정자동 뺵다방 앞에 불 났어요.
                규모 및 상황 : 총 5명이 다쳤고 불이 계속 번지고 있어요.
                신고자 정보 : 저는 뺵다방 앞 스타벅스 직원이에요
            '''

    # 질의
    question = '사건 발생 지역이 어디야?'
                # 사건 발생 지역이 어디야?
                # 사건의 규모와 상황좀 알려줘
                # 신고자 정보좀 알려줘
                
                # 해당 사건 신고를 처리해야할 부서가 소방서, 경찰서, 민원처리실 중 어디야? (X)
                # 해당 사건의 종류가 뭐야 (x)
    
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
    
    # ETRI 응답 Text 복호화
    data = json.loads(response.data.decode("utf-8", errors='ignore'))
    
    print('화재 장소 추정 : ', data['return_object']['MRCInfo']['answer'])
    
    # ETRI 응답 Text Return
    return HttpResponse(data['return_object']['MRCInfo']['answer'])




# 현재 상황: 빽다방에 불이 났으며 불이 점점 커지고 있음

# 사건 발생 장소: 분당 KT 건너편 빽다방

# 사상자: 총 5명

# 신고자: 해당 매장 직원

# 중증 환자 여부: 가스 흡입으로 생명 위독한 1명
# 날씨: X

# 아직 알지 못한 정보 :  ['날씨']


'''
분당 KT 건너편 빽다방에 불났어요.
총 5명이 다쳤고 1명은 가스 흡입으로 생명이 위독해요. 
현재 불이 점점더 커지고 있고 저는 해당 매장 직원이에요.
'''






#######################################  GPT  #########################################################
from openai import OpenAI
import os

from stt.views import recognize_speech
# GPT API key 가져오기
api_key = os.getenv("OPENAI_API_KEY")

record = ''
requirements = ['사건 분류', '사건 발생 장소', '구체적인 현장 상태']
info = {'사건 분류' : 'X', '사건 발생 장소' : 'X', '구체적인 현장 상태' : 'X'}

def gpt_api(request):
    
    global record, info
    
    # 신고자 음성 정보 (단발성)
    sentence = '분당 KT 건너편 빽다방에 불났어요. 총 5명이 다쳤고 1명은 가스 흡입으로 생명이 위독해요. 현재 불이 점점더 커지고 있어요.'
    # sentence = '불났어요. 총 5명이 다쳤고 1명은 가스 흡입으로 생명이 위독해요. 현재 불이 점점더 커지고 있어요.'
    sentence = recognize_speech()
    # 전체 통화 내용 기록
    record += sentence
    
    # 신고자에게 요청할 필수 정보
    print(requirements)
    
    # OpenAI GPT API 를 활용하여 명령 하달
    command = record + """위 긴급 구조 신고 전화 내용을 분석하여, '사건 분류', '사건 발생 장소', '구체적인 현장 상태'에 관해 각각 답변해줘.
                        만약 특정 답변을 생성하기에 정보가 부족하다면, 해당 정보는 X를 답변해줘.
                        예를들어 '여기 불났어요' 라는 신고가 발생하면, 사건 분류 : 화재, 사건 발생 장소 : X, 구체적인 현장 상태 : X 를 리턴해주면돼."""
    
    print(command)
    
    # GPT API
    client = OpenAI(api_key = api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": command}  # 음성 인식으로 변환된 텍스트 입력
        ],
        temperature = 0.5,
        top_p = 0.5,
    )
    
    # GPT 가 응답한 메시지
    message = response.choices[0].message.content.split('\n')
    print(message)
    
    li = []
    # 필요한 정보 전처리 및 정제
    for ele in message:
        
        key, value = ele.split(':')
        key, value = key.strip(), value.strip()
        
        info[key] = value
        
        if value == 'X':
            li.append(key)
        
        
    print(info)
    print(li)
    
    if not li:
        event = EmergencyCalls()
        event.category = info['사건 분류']
        event.location = info['사건 발생 장소']
        event.details = info['구체적인 현장 상태']
        
        # event.estimated_address = get_address(info['사건 발생 장소'])  여기를 수정해달라
        event.save()
        
    return info





def get_address(query):
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {settings.KAKAO_API_KEY}"
    }
    params = {
        "query": query
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        documents = result.get("documents", [])
        if documents:
            address_name = documents[0].get("address_name")
            return address_name
        else:
            return None
    else:
        return None