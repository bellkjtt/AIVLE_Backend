import os
import torch
import numpy as np
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Model1 Class
class Model1:
    def __init__(self, model_path, checkpoint, tokenizer_name):
        self.config = AutoConfig.from_pretrained(os.path.join(model_path, checkpoint))
        self.tokenizer = AutoTokenizer.from_pretrained(os.path.join(model_path, tokenizer_name))
        self.tokenizer.model_max_length = 512  # 또는 config에서 지정된 최대 길이
        self.model = AutoModelForSequenceClassification.from_pretrained(
            os.path.join(model_path, checkpoint),
            config=self.config,
        )
        self.model = self.model.to(device)
        self.model.eval()
        self.device = device

# Model2 Class
class Model2:
    def __init__(self, model_link, ckpt_path, class_num=2):
        from model2.model import Baseline
        self.tokenizer = AutoTokenizer.from_pretrained(model_link)
        self.model = Baseline(model_link=model_link, class_num=class_num)
        self.criterion = torch.nn.CrossEntropyLoss()
        
        self.device = device
        self.inference_label_frequency= 0.30287 # 적절한 threshold 정하기
        # 기타 설정
        ckpt = torch.load(ckpt_path, map_location=device)
        self.model.load_state_dict(ckpt['model_state_dict'], strict=False)
        self.model.to(device)
        self.model.eval()

