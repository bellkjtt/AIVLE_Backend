record = ''
info = {'사건 정보' : 'X', '사건 발생 장소' : 'X', '사상자' : 'X', '신고자' : 'X', '중증 환자 여부' : 'X', '날씨' : 'X'}

print(info)



def gpt_api():
    
    global record, info
    
    # 신고자 음성 정보 (단발성)
    sentence = '분당 KT 건너편 빽다방에 불났어요. 총 5명이 다쳤고 1명은 가스 흡입으로 생명이 위독해요. 현재 불이 점점더 커지고 있고 저는 해당 매장 직원이에요.'
    
    # 전체 통화 내용 기록
    record += sentence
    
    # 신고자에게 요청할 필수 정보
    requirements = info.keys()
    print(requirements)
    
    
    # OpenAI GPT API 를 활용하여 명령 하달
    command = sentence + """
                            \n 
                            해당 문자열을 분석하고, 내가 요구하는 정보들에 대해 각각 응답해줘.
                            만약 문자열에 있는 정보만으로 응답 할 수 없다면, 해당 요구 정보에는 X를 응답해줘
                            예를들어, ['사건 정보', '사건 발생 장소', '사상자'] 정보를 요구한다면
                            각각에 해당하는 응답을 생성해주면돼.
                            모두 알 수 없다면 {'사건 정보' : 'X', '사건 발생 장소' : 'X', '사상자' : 'X' } 사전 형태로 응답하고
                            날씨 정보만 알 수 없다면 {'사건 정보' : 'X', '사건 발생 장소' : 'X', '사상자' : 'X' } 사전 형태로 응답해.
                            
                            요구정보 : """ + str(requirements)[10:-1]
    
    # print(command)
    message = "{'사건 정보': '화재', '사건 발생 장소': '분당 KT 건너편 빽다방', '사상자': 5, '신고자': '해당 매장 직원', '중증 환자 여부': '가스 흡입으로 생명이 위독한 1명', '날씨': 'X'}"
    message = message[1:-1]
    li = message.split(',')
    for ele in li:
        key, value = ele.split(':')
        
        if value != 'X':
            info[key] = value
            
    print(info)
    # # GPT API
    # client = OpenAI(api_key = api_key)
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": command}  # 음성 인식으로 변환된 텍스트 입력
    #     ]
    # )
    
gpt_api()
#     # 신고자에게 요청할 필수 정보
#     requirements = '사건 정보, 사건 발생 장소, 사상자, 신고자, 중증 환장 여부, 날씨'
    
#     
    
#     # GPT 가 응답한 메시지
#     message = response.choices[0].message
    
#     # GPT 가 응답한 메시지 정제
#     message = message.content.split('\n')
#     print(message)
    
#     for ele in message:
        
#         print(ele)
        
#         if (ele == '{') or (ele == '}'):
#             pass
        
#         else:
#             key, value = ele.split(':')
#             key = key.strip()
#             key = key[1:-1]
#             value = value.strip()
#             value = value[1:-1]
#             info[key] = value

#     print('---------------------')
#     print(info)

    
#     print('---------------------')
#     # 아직 알 수 없는 정보
#     unknownData =[]
#     for key, val in info.items():
#         if val == "X":
#             unknownData.append(key)
    
#     print(unknownData)
    
#     # 아직 정보 부족함
#     if not unknownData:
#         print('모든 요구 정보 알아냄')
#         print()
        
#         print('-----------record------------')
#         print(record)
#         print()
        
#         print('-----------info------------')
#         print(info)
    
#     # 모든 요구 정보 확인
#     else:
#         print('아직', unknownData, '정보 없음')
    
#     return HttpResponse('ok')