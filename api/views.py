import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split, RandomSampler

from .models import Result

# Backend (Django views.py)
import numpy as np
from django.http import JsonResponse
from rest_framework.views import APIView
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer
import torch
from transformers import pipeline
import io
import os

# from model2.dataset import *
# # from model2.learning import *
# from model2.model import *

# # 저장된 모델과 토크나이저 로드(16종 분류)
# model_path = "./finetuned_models"

# import os

# # ffmpeg 경로 설정
# os.environ["PATH"] += os.pathsep + r"C:/ffmpeg/bin"


# config = AutoConfig.from_pretrained(os.path.join(model_path,'checkpoint-11500'))

# tokenizer = AutoTokenizer.from_pretrained(os.path.join(model_path,'KcELECTRA-base-v2022'))
# tokenizer.model_max_length = 512  # 또는 config에서 지정된 최대 길이
# # 모델 로드
# model = AutoModelForSequenceClassification.from_pretrained(
#     os.path.join(model_path,'checkpoint-11500'),
#     config=config,
# )

# # GPU 사용 가능 여부 확인
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)

# # 모델을 평가 모드로 설정
# model.eval()


# SEED = 42
# # random.seed(SEED) #  Python의 random 라이브러리가 제공하는 랜덤 연산이 항상 동일한 결과를 출력하게끔
# os.environ['PYTHONHASHSEED'] = str(SEED)
# np.random.seed(SEED)
# torch.manual_seed(SEED)
# torch.cuda.manual_seed(SEED)
# torch.backends.cudnn.deterministic = True
# #두번째 모델 - 구급/비구급 분류
# model_link = 'beomi/KcELECTRA-base-v2022' #'beomi/kcbert-base'
#  # epochs = 15
# batch_size = 512 + 256
# class_num = 2
# max_length = 256 # 384
# padding = 'max_length'

# inference_label_frequency = 0.30287 # 적절한 threshold 정하기

# tokenizer2 = AutoTokenizer.from_pretrained(model_link)

# ckpt_path = os.path.join('model2','checkpoint_2_300.tar') # chceck your path
    
# file_name = os.path.basename(ckpt_path).split('.')[0]
# model2 = Baseline(model_link=model_link, class_num=2)
# criterion = torch.nn.CrossEntropyLoss()



# ckpt = torch.load(ckpt_path, map_location=device)
# model2.load_state_dict(ckpt['model_state_dict'], strict=False);  ######## 여기야 여기
# model2.to(device); 
# model2.eval()                                            


# # Whisper 모델 로드 (Hugging Face Hub에서 로드)
# whisper_model = pipeline("automatic-speech-recognition", model="openai/whisper-base")

# # # 음성 파일을 텍스트로 변환하는 함수
# # def speech_to_text(audio_file):
# #     audio_bytes = audio_file.read()
# #     # Whisper 모델로 음성을 텍스트로 변환
# #     result = whisper_model(audio_bytes)
# #     return result['text']
# def speech_to_text(audio_file):
#     import urllib3
#     import json
#     import base64
#     openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
#     accessKey = "ab05b686-9393-4740-a866-9e85c4569fec"
#     languageCode = "korean"
    
#     file = audio_file
#     audioContents = base64.b64encode(file.read()).decode("utf8")
#     file.close()
    
#     requestJson = {    
#         "argument": {
#             "language_code": languageCode,
#             "audio": audioContents
#         }
#     }
    
#     http = urllib3.PoolManager()
#     response = http.request(
#         "POST",
#         openApiURL,
#         headers={"Content-Type": "application/json; charset=UTF-8","Authorization": accessKey},
#         body=json.dumps(requestJson)
#     )
#     response_data = json.loads(response.data.decode("utf-8"))
#     recognized_text = response_data["return_object"]["recognized"]
#     return recognized_text


# #두번쨰 모델 - 긴급도 분류

# def classify_text(text):
#     # 입력 텍스트를 토큰화하고 모델 입력 형식으로 변환
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
#     inputs = {k: v.to(device) for k, v in inputs.items()}
    
#     # 모델 추론
#     with torch.no_grad():
#         outputs = model(**inputs)
#         logits = outputs.logits
#         probabilities = torch.nn.functional.softmax(logits, dim=-1)
#         predicted_class = torch.argmax(probabilities, dim=-1).item()
    
#     print(probabilities)
    
#     # 결과 해석
#     predicted_label = config.id2label[predicted_class]
#     confidence = probabilities[0][predicted_class].item()
    
#     return predicted_label, confidence


# def classify_text2(text, tokenizer, model, device, label_frequency=None):
#     # 입력 텍스트를 토큰화하고 모델 입력 형식으로 변환
#     custom_labels = {0: "비구급", 1: "구급"}  # 0: 비긴급, 1: 긴급
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=padding, max_length=max_length)
#     if label_frequency: 
#         input_ids = inputs['input_ids'].to(device)
#         attention_mask = inputs['attention_mask'].to(device)
#         token_type_ids = inputs['token_type_ids'].to(device)
#     else:
#         inputs = {k: v.to(device) for k, v in inputs.items()}
#     # 모델 추론
#     with torch.no_grad():
#         if label_frequency:
#             outputs = model(input_ids, attention_mask, token_type_ids)
#             logits = outputs
#             probabilities = torch.nn.functional.softmax(logits, dim=-1)
#             print(probabilities)
#             predicted_class = (probabilities[0, 1] >= label_frequency).int().item()
#             # predicted_labels = torch.where(probabilities >= label_frequency , 1, 0)
#             # print(predicted_class)
#             predicted_label = custom_labels[predicted_class]
#             confidence = probabilities[0][predicted_class].item()      
#         else:
#             outputs = model(**inputs)
#             logits = outputs.logits
#             probabilities = torch.nn.functional.softmax(logits, dim=-1)
#             predicted_class = torch.argmax(probabilities, dim=-1).item()
#             predicted_label = config.id2label[predicted_class]           # 결과 해석
#             confidence = probabilities[0][predicted_class].item()
    
#     return predicted_label, confidence

# # APIView 정의
# class PredictView(APIView):
#     def post(self, request, *args, **kwargs):
#         audio_file = request.FILES.get("audio")
#         if not audio_file:
#             return JsonResponse({"error": "No audio file provided"}, status=400)
        
#         text = speech_to_text(audio_file)
#         if not text:
#             return JsonResponse({"error": "Failed to transcribe audio"}, status=500)
#         #text='숨을 쉬지 않아요.'                                                       ##
#         # prediction, conf = classify_text(text)
#         prediction, conf =classify_text2(text, tokenizer, model, device)
#         print(prediction,conf)
#         prediction2, conf2 =classify_text2(text, tokenizer2, model2, device,inference_label_frequency)
#         print(text)
#         print(prediction2,conf2)
#         return JsonResponse({
#             "transcription": text,
#             "prediction": prediction,
#             "confidence": float(conf),
#             "prediction2" : prediction2,
#             "confidence2": float(conf2),
#         })
        
        
from rest_framework.response import Response    
class Disaster(APIView):
    def get(self, request):
        disasters = Result.objects.values_list('disaster_large', flat=True)
        return Response(disasters)