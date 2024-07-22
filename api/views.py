import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split, RandomSampler

# from .models import Result
import sys

# Backend (Django views.py)
import numpy as np
from django.http import JsonResponse
from rest_framework.views import APIView
import io
import os
from .classify_model import Model1,Model2

# 설정
model_path = "./finetuned_models"
checkpoint = 'checkpoint-11500'
tokenizer_name = 'KcELECTRA-base-v2022'

# 모델1 초기화
model1 = Model1(model_path=model_path, checkpoint=checkpoint, tokenizer_name=tokenizer_name)

# 모델2 초기화
model_link = 'beomi/KcELECTRA-base-v2022'
ckpt_path = os.path.join('model2', 'checkpoint_2_300.tar')
model2 = Model2(model_link=model_link, ckpt_path=ckpt_path)

padding = 'max_length'

SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic = True


def speech_to_text(audio_file):
    import urllib3
    import json
    import base64
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
    accessKey = "ab05b686-9393-4740-a866-9e85c4569fec"
    languageCode = "korean"
    
    file = audio_file
    audioContents = base64.b64encode(file.read()).decode("utf8")
    file.close()
    
    requestJson = {    
        "argument": {
            "language_code": languageCode,
            "audio": audioContents
        }
    }
    
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8","Authorization": accessKey},
        body=json.dumps(requestJson)
    )
    response_data = json.loads(response.data.decode("utf-8"))
    recognized_text = response_data["return_object"]["recognized"]
    return recognized_text

#두번쨰 모델 - 긴급도 분류
def classify_text(text, tokenizer, model, device, label_frequency=None):
    # 입력 텍스트를 토큰화하고 모델 입력 형식으로 변환
    custom_labels = {0: "비구급", 1: "구급"}  # 0: 비긴급, 1: 긴급
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=padding, max_length=model.tokenizer.model_max_length)
    if label_frequency: 
        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)
        token_type_ids = inputs['token_type_ids'].to(device)
    else:
        inputs = {k: v.to(device) for k, v in inputs.items()}
    # 모델 추론
    with torch.no_grad():
        if label_frequency:
            outputs = model.model(input_ids, attention_mask, token_type_ids)
            logits = outputs
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            print(probabilities)
            predicted_class = (probabilities[0, 1] >= label_frequency).int().item()
            # predicted_labels = torch.where(probabilities >= label_frequency , 1, 0)
            # print(predicted_class)
            predicted_label = custom_labels[predicted_class]
            confidence = probabilities[0][predicted_class].item()      
        else:
            outputs = model.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            predicted_label = model.config.id2label[predicted_class]           # 결과 해석
            confidence = probabilities[0][predicted_class].item()
    
    return predicted_label, confidence

# APIView 정의
class PredictView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.POST.get("full_text", '')
        # if not audio_file:
        #     return JsonResponse({"error": "No audio file provided"}, status=400)
        
        # text = speech_to_text(audio_file)
        # text='숨을 쉬지 않아요.'  
        if not text:
            return JsonResponse({"error": "Failed to transcribe audio"}, status=500)
                                                             ##
        # prediction, conf = classify_text(text)
        prediction, conf =classify_text(text, model1.tokenizer, model1, model1.device)
        print(prediction,conf)
        prediction2, conf2 =classify_text(text, model2.tokenizer, model2, model2.device,model2.inference_label_frequency)
        print(text)
        print(prediction2,conf2)
        return JsonResponse({
            "transcription": text,
            "prediction": prediction,
            "confidence": float(conf),
            "prediction2" : prediction2,
            "confidence2": float(conf2),
        })
        
