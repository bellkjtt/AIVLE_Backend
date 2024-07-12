from openai import OpenAI
import os

# GPT API key 가져오기
api_key = os.getenv("OPENAI_API_KEY")

def get_gpt_response(text):
    # OpenAI API 인스턴스 생성 시 API 키 전달
    client = OpenAI(api_key=api_key)

    text += "\n해당 문자열을 분석해서 " + plus + "를 출력해줘. 문자열에 정보가 없는 거는 X로 출력해줘. X일시 X만 출력하고 다른 말은 추가하지 마"
    print(text)
    
    # GPT API에 대화 요청 보내기
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}  # 음성 인식으로 변환된 텍스트 입력
        ]
    )

    return response.choices[0].message


# 텍스트 입력
text = '분당 KT 건너편 빽다방에 불났어요. 총 5명이 다쳤고 1명은 가스 흡입으로 생명이 위독해요. 현재 불이 점점더 커지고 있고 저는 해당 매장 직원이에요.'
plus = '현재 상황, 사건 발생 장소, 사상자, 신고자, 중증 환장 여부, 날씨'

# GPT API 호출하여 필요한 정보 추출
message = get_gpt_response(text)


print(message.content)



# API 응답에서 필요한 정보 추출
info = {}

message = message.content.split('\n')

for ele in message:
    key, value = ele.split(':')
    key = key.strip()
    value = value.strip()
    info[key] = value

li =[]
for key, val in info.items():
    if val == 'X':
        li.append(key)

print('아직 알지 못한 정보 : ', li)