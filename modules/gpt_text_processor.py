## GPT API를 활용하여 데이터 정제 모듈 파일 ##

import sys
import os
import django
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from openai import OpenAI                                       # GPT API
from modules.estimate_address import get_address                # 신고 위치(주소, 장소) 추정
from modules.check_duplication import check_duplication         # 신고 위치(주소, 장소) 추정
# from modules.classification_model import ClassificationModel    # 신고 위치(주소, 장소) 추정

# classifcation = ClassificationModel()

# GPT Text 정제 클래스
class GPTProcessor:


    # 인스턴스 선언 (OPENAI_API_KEY)
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")  # GPT API key
        self.record = ''                              # 새로운 신고 전화
        self.requirements = {'사건 분류': 'X', '사건 발생 장소': 'X', '구체적인 현장 상태': 'X'}
        

    # 데이터 정제를 위한 전처리
    def text_preprocessor(self, sentence):

        # 전체 대화 기록
        self.record += '\n' + sentence
        
        # 신고자가 제공한 현재까지 음성 정보
        print()
        print('[신고 음성 기록]', self.record)

        # GPT 명령 하달
        command = self.record + "위 긴급 구조 신고 전화 내용을 분석하여, '사건 분류', '사건 발생 장소', '구체적인 현장 상태'에 관해 각각 답변해줘. 만약 특정 답변을 생성하기에 정보가 부족하다면, 해당 정보는 X를 답변해줘. 예를들어 '여기 불났어요' 라는 신고가 발생하면, 사건 분류 : 화재, 사건 발생 장소 : X, 구체적인 현장 상태 : X 를 리턴해주면돼."
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": command}  # 음성 인식으로 변환된 텍스트 입력
            ],
            temperature=0.5,
            top_p=0.5,
        )

        # GPT 응답
        message = response.choices[0].message.content.split('\n')

        # 필요 데이터 전처리 및 정제
        unknown_li = []
        for ele in message:
            try:
                key, value = ele.split(':')
                key, value = key.strip(), value.strip()
                self.requirements[key] = value
                if value == 'X':
                    unknown_li.append(key)
            
            except:
                # print('GPT API 오작동 (다시 한번 말씀해주세요)')
                return 'GPT API 오작동 (다시 한번 말씀해주세요)', None


        ################# Debugging Test ################
        # print()
        # print('데이터 정제 :', self.requirements)
        # print()
        # print('미확인된 정보 : ', unknown_li)
        ################# Debugging Test ################

        
        # 모든 필수 정보를 알아냈다.
        if not unknown_li:


            # 상세 위치(장소, 주소) 추정
            estimateAddress = get_address(self.requirements['사건 발생 장소'])

            if estimateAddress == "Index_Error":
                return "사건 발생 장소를 다시 한번 말해주세요.", None
            
            address_name = estimateAddress['추정 주소'] if estimateAddress else 'X'
            place_name = estimateAddress['추정 장소'] if estimateAddress else 'X'
            phone_number = estimateAddress['추정 번호'] if estimateAddress else 'X'
            lat = estimateAddress['위도'] if estimateAddress else 'X'
            lng = estimateAddress['경도'] if estimateAddress else 'X'

            category = self.requirements['사건 분류']
            location = self.requirements['사건 발생 장소']
            details = self.requirements['구체적인 현장 상태']

            context = {
                '사건 분류': category,
                '사건 발생 장소': location,
                '구체적인 현장 상태': details,
                '추정 주소': address_name,
                '추정 장소': place_name,
                '추정 번호': phone_number,
                '위도' : lat,
                '경도' : lng,
            }
            
            # 중복 신고 여부 확인
            is_duplicate = check_duplication(context)
            
            # 중복이 아닌 신고
            if not is_duplicate:
                print('신고가 접수되었습니다.')
                
                
                # a = classifcation.classificate(self.record)
                
                # print(a)
                print()
                print('--------------------------------------------------')
                print('[신고 내용 정제]')
                print(context)
                return '신고가 접수되었습니다.', context
            
            # 중복 신고
            else:
                # print('이미 접수된 신고입니다.')
                # print(context)
                return '이미 접수된 신고입니다.', context
        
        # 더 많은 정보가 필요함
        else:
            information = ' '.join(unknown_li)
            return f'신고 접수를 위해 추가로 필요한 정보 : {information}', None




# 단독 모듈 Test
if __name__ == "__main__":
    processor = GPTProcessor()
    
    # 장소 정보 제공 X
    processor.text_preprocessor('사람이 칼에 맞아 쓰려졌어요. 피가 너무 많이 나요')
    print()

    print('-' * 50)
    
    # 이후에 장소 정보 제공
    processor.text_preprocessor('여기는 정자역 빽다방이에요.')
    print()