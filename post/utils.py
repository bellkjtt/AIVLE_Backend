from django.http import JsonResponse
from stt.models import CallLogs
from django.core.serializers import serialize
import json


# 데이터 가져오기
def get_data():
    
    # 데이터 검색
    data = CallLogs.objects.filter(is_duplicate=0).order_by('-date')
    
    # 데이터를 JSON 형식으로 직렬화
    json_data = serialize('json', data)
    
    # JSON 데이터를 Python 객체로 변환
    json_data = json.loads(json_data)
    
    return json_data

# 데이터 전송
def send(request):
    json_data = get_data()
    print(json_data)
    return JsonResponse(json_data, safe=False)