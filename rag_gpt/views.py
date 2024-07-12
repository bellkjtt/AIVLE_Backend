from django.shortcuts import render, HttpResponse

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

# GPT API key 가져오기
api_key = os.getenv("OPENAI_API_KEY")





def gpt_api(request):
    
    
    # 텍스트 입력
    text = '분당 KT 건너편 빽다방에 불났어요. 총 5명이 다쳤고 1명은 가스 흡입으로 생명이 위독해요. 현재 불이 점점더 커지고 있고 저는 해당 매장 직원이에요.'
    plus = '현재 상황, 사건 발생 장소, 사상자, 신고자, 중증 환장 여부, 날씨'


    # OpenAI API 인스턴스 생성 시 API 키 전달
    client = OpenAI(api_key=api_key)

    text += "\n해당 문자열에서 " + plus + "를 출력해주세요. 모르면 X로 출력해주세요. X일시 X만 출력하고 다른 말은 추가하지 마세요"
    print(text)
    
    # GPT API에 대화 요청 보내기
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}  # 음성 인식으로 변환된 텍스트 입력
        ]
    )
    
    # GPT API 호출하여 필요한 정보 추출
    message = response.choices[0].message
    
    # API 응답에서 필요한 정보 추출
    info = {}

    # 대화 분할
    message = message.content.split('\n')


    # 필요한 정보 정제
    for ele in message:
        key, value = ele.split(':')
        key = key.strip()
        value = value.strip()
        info[key] = value


    # 아직 알 수 없는 정보
    li =[]
    for key, val in info.items():
        if val == 'X':
            li.append(key)

    
    print(info)
    print('아직 알지 못한 정보 : ', li)
    
    return HttpResponse('ok')