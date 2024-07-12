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
