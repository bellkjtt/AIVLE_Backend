## 중복 신고 판단 모듈 파일 ##

import sys
import os
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rag_gpt.models import EmergencyCalls


# 이미 신고된 사건인지 중복 검사
def check_duplication(context):

    # 중복 기준 : 사건 분류, 사건 발생 장소
    category = context['사건 분류']
    address_name  = context['추정 주소']
    
    # 중복 여부 (Bool 타입)
    is_duplicate = EmergencyCalls.objects.filter(category=category, address_name=address_name).exists()
    
    if is_duplicate:
        pass
    
    # 새로운 정보 DB 정제
    else:
        record = EmergencyCalls()
        record.category = context['사건 분류']
        record.location = context['사건 발생 장소']
        record.details = context['구체적인 현장 상태']
        record.address_name = context['추정 주소']
        record.place_name = context['추정 장소']
        record.phone_number = context['추정 번호']
        record.save()
        
    return is_duplicate





# 모듈 단독 Test
if __name__ == "__main__":
    
    # 예시
    test_context = {
        '사건 분류': '화재',
        '사건 발생 장소': '서울역 스타벅스',
        '구체적인 현장 상태': '연기가 많이 나고 있음',
        '추정 주소': '서울특별시 용산구 한강대로 405',
        '추정 장소': '서울역 스타벅스',
        '추정 번호': '02-123-4567'
    }
    
    result = check_duplication(test_context)
    
    if result:
        print("정보 중복 처리")
    else:
        print("새로운 정보 등록")
