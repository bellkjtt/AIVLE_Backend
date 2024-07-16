# import os
# import json
# import base64
# import wave
# import pyaudio
# import threading
# import queue
# import urllib3
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from django.shortcuts import render

# def index(request):
#     return render(request, 'index.html')

# # 설정
# CHUNK = 1024  # 버퍼 크기
# FORMAT = pyaudio.paInt16  # 음성 포맷
# CHANNELS = 1  # 모노 채널
# RATE = 16000  # 샘플링 레이트
# RECORD_SECONDS = 1  # 녹음 시간 단위 (1초)
# WAVE_OUTPUT_FILENAME = "output.wav"  # 전체 저장할 파일 이름

# # ETRI API 설정
# openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
# accessKey = "2b233e5f-a9c9-4224-989a-5b3d781f3385"
# languageCode = "korean"

# # 전역 변수
# recording = False
# audio_queue = queue.Queue()
# frames = []

# def recognize_with_etri(audio_data):
#     audio_contents = base64.b64encode(audio_data).decode("utf8")
    
#     request_json = {
#         "argument": {
#             "language_code": languageCode,
#             "audio": audio_contents
#         }
#     }
    
#     http = urllib3.PoolManager()
#     response = http.request(
#         "POST",
#         openApiURL,
#         headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
#         body=json.dumps(request_json)
#     )
    
#     response_data = json.loads(response.data.decode("utf-8"))
#     return response_data

# @method_decorator(csrf_exempt, name='dispatch')
# class StartRecordingAPIView(APIView):

#     def post(self, request, *args, **kwargs):
#         global recording
#         if recording:
#             return Response({"error": "Recording is already in progress."}, status=status.HTTP_400_BAD_REQUEST)
        
#         recording = True
        
#         def audio_recorder():
#             p = pyaudio.PyAudio()
#             stream = p.open(format=FORMAT,
#                             channels=CHANNELS,
#                             rate=RATE,
#                             input=True,
#                             frames_per_buffer=CHUNK)
            
#             print("Recording...")
#             try:
#                 while recording:
#                     audio_data = []
#                     for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#                         data = stream.read(CHUNK)
#                         audio_data.append(data)
                    
#                     audio_data = b''.join(audio_data)
#                     frames.append(audio_data)
#                     audio_queue.put(audio_data)
#             except Exception as e:
#                 print("Recording error:", e)
#             finally:
#                 stream.stop_stream()
#                 stream.close()
#                 p.terminate()
#                 audio_queue.put(None)
        
#         def process_audio():
#             while True:
#                 audio_data = audio_queue.get()
#                 if audio_data is None:
#                     break
                
#                 response = recognize_with_etri(audio_data)
#                 if response.get('result') == 0:
#                     text = response['return_object']['recognized']
#                     print("Recognized text: ", text)
#                 else:
#                     print("Error recognizing audio with ETRI API")
        
#         recording_thread = threading.Thread(target=audio_recorder)
#         processing_thread = threading.Thread(target=process_audio)
        
#         recording_thread.start()
#         processing_thread.start()
        
#         return Response({"message": "Recording started."}, status=status.HTTP_200_OK)

# @method_decorator(csrf_exempt, name='dispatch')
# class StopRecordingAPIView(APIView):

#     def post(self, request, *args, **kwargs):
#         global recording, frames
#         if not recording:
#             return Response({"error": "Recording is not in progress."}, status=status.HTTP_400_BAD_REQUEST)
        
#         recording = False
#         # 전체 녹음 데이터 저장
#         with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
#             wf.setnchannels(CHANNELS)
#             wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
#             wf.setframerate(RATE)
#             wf.writeframes(b''.join(frames))
        
#         # frames 초기화
#         frames = []
#         return Response({"message": "Recording stopped and saved as " + WAVE_OUTPUT_FILENAME}, status=status.HTTP_200_OK)


import os
import pyaudio
import wave
import threading
import requests
import time
import queue
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import numpy as np


# 네이버 클로바 스피치 API 설정
client_id = "etu7ckegx5"
client_secret = "4WtVsc9mDlMZJmsrswHcZIaOlW2Fz200DMAmEFvO"
lang = "Kor"  # 언어 코드 (한국어: Kor)
url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang

# 오디오 설정
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500  # 무음 감지 임계값
SILENCE_DURATION = 3  # 무음이 일정 시간 이상 지속되면 (초)
WAVE_OUTPUT_FILENAME = "output.wav"
FULL_CONVERSATION_FILENAME = "full_conversation.wav"

# PyAudio 초기화
audio = pyaudio.PyAudio()

# 오디오 큐 초기화
audio_queue = queue.Queue()

# 전역 변수
recording = False
silence_start = None
text=''

# 음성파일 클로바 API로 보내서 텍스트 받아옴
def recognize_speech(file_path):
    global text
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    with open(file_path, 'rb') as data:
        response = requests.post(url, data=data, headers=headers)
    rescode = response.status_code
    if rescode == 200:
        text = response.json().get('text', 'No text recognized')
        print("Recognized text:", text)
    else:
        print("Error:", response.text)
        
# 전체 녹음 저장
def continuous_recording():
    global recording
    wf_full = wave.open(FULL_CONVERSATION_FILENAME, 'wb')
    wf_full.setnchannels(CHANNELS)
    wf_full.setsampwidth(audio.get_sample_size(FORMAT))
    wf_full.setframerate(RATE)

    #큐에 오디오 넣기
    def callback(in_data, frame_count, time_info, status):
        if not recording:
            return in_data, pyaudio.paComplete
        wf_full.writeframes(in_data)
        audio_queue.put(in_data)
        return in_data, pyaudio.paContinue
    #녹음 시작
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=callback)

    print("Recording...")
    stream.start_stream()

    while recording:
        time.sleep(0.1)
    #녹음 끝
    stream.stop_stream()
    stream.close()
    wf_full.close()
    print("Recording stopped")

#무음 감지 후 recognize
def detect_silence_and_recognize():
    global recording, silence_start
    frames = []

    #무음감지
    def is_silence(data):
        return np.max(np.frombuffer(data, dtype=np.int16)) < SILENCE_THRESHOLD

    # 녹음된 음성이 존재하면 output.wav로 저장후 recognize_speech 함수 실행
    def save_and_recognize():
        nonlocal frames
        if frames:
            filename = "output.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            frames = []

            recognize_speech(filename)

    while recording:
        if not audio_queue.empty():
            data = audio_queue.get()
            frames.append(data)

            #무음 감지시 save_and_recognize 함수 실행
            if is_silence(data):
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    print("Silence detected, saving and recognizing")
                    save_and_recognize()
                    silence_start = None
            else:
                silence_start = None

    save_and_recognize()

def index(request):
    return render(request, 'index.html')

#녹음시작 버튼을 누르면 멀티스레드를 활용해 녹음 시작
@method_decorator(csrf_exempt, name='dispatch')
class StartRecordingAPIView(View):
    def post(self, request, *args, **kwargs):
        global recording
        if recording:
            return JsonResponse({"error": "Recording is already in progress."}, status=400)

        recording = True

        record_thread = threading.Thread(target=continuous_recording)
        silence_detect_thread = threading.Thread(target=detect_silence_and_recognize)

        record_thread.start()
        silence_detect_thread.start()

        return JsonResponse({"message": "Recording started."}, status=200)

#녹음 끝
@method_decorator(csrf_exempt, name='dispatch')
class StopRecordingAPIView(View):
    def post(self, request, *args, **kwargs):
        global recording
        if not recording:
            return JsonResponse({"error": "Recording is not in progress."}, status=400)

        recording = False
        return JsonResponse({"message": "Recording stopped."}, status=200)


# import os
# import pyaudio
# import wave
# import threading
# import requests
# import time
# import queue
# from datetime import datetime
# from django.http import JsonResponse
# from django.views import View
# from django.shortcuts import render
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# import numpy as np
# import azure.cognitiveservices.speech as speechsdk
# from pydub import AudioSegment

# # Azure Speech 서비스 설정
# subscription_key = "b38d939a8d944b2892650b263aa77be6"
# region = "koreacentral"

# # 오디오 설정
# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# SILENCE_THRESHOLD = 500  # 무음 감지 임계값
# SILENCE_DURATION = 3  # 무음이 일정 시간 이상 지속되면 (초)
# FULL_CONVERSATION_FILENAME = "full_conversation.wav"

# # PyAudio 초기화
# audio = pyaudio.PyAudio()

# # 오디오 큐 초기화
# audio_queue = queue.Queue()

# # 전역 변수
# recording = False
# silence_start = None

# def recognize_with_azure(audio_file_path):
#     # Speech Config 설정 및 언어 설정 (한국어)
#     speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
#     speech_config.speech_recognition_language = "ko-KR"

#     # Audio Config 설정
#     audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

#     # Speech recognizer 생성
#     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

#     # 인식 결과를 저장할 변수
#     result_text = []

#     def recognized(evt):
#         result_text.append(evt.result.text)

#     # 인식된 결과를 콜백 함수에 연결
#     speech_recognizer.recognized.connect(recognized)

#     # 음성 파일을 인식 시작
#     speech_recognizer.start_continuous_recognition()
    
#     # 인식 종료를 기다립니다. (이 예제에서는 30초 동안 인식합니다)
#     import time
#     time.sleep(30)

#     # 인식 종료
#     speech_recognizer.stop_continuous_recognition()

#     return " ".join(result_text)

# def preprocess_audio(input_path, output_path):
#     audio = AudioSegment.from_wav(input_path)
#     audio = audio.set_frame_rate(16000)
#     audio = audio.set_channels(1)
#     audio.export(output_path, format="wav")

# def continuous_recording():
#     global recording
#     wf_full = wave.open(FULL_CONVERSATION_FILENAME, 'wb')
#     wf_full.setnchannels(CHANNELS)
#     wf_full.setsampwidth(audio.get_sample_size(FORMAT))
#     wf_full.setframerate(RATE)

#     def callback(in_data, frame_count, time_info, status):
#         if not recording:
#             return in_data, pyaudio.paComplete
#         wf_full.writeframes(in_data)
#         audio_queue.put(in_data)
#         return in_data, pyaudio.paContinue

#     stream = audio.open(format=FORMAT,
#                         channels=CHANNELS,
#                         rate=RATE,
#                         input=True,
#                         frames_per_buffer=CHUNK,
#                         stream_callback=callback)

#     print("Recording...")
#     stream.start_stream()

#     while recording:
#         time.sleep(0.1)

#     stream.stop_stream()
#     stream.close()
#     wf_full.close()
#     print("Recording stopped")

# def detect_silence_and_recognize():
#     global recording, silence_start
#     frames = []

#     def is_silence(data):
#         return np.max(np.frombuffer(data, dtype=np.int16)) < SILENCE_THRESHOLD

#     def save_and_recognize():
#         nonlocal frames
#         if frames:
#             raw_filename = f"output_raw_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
#             processed_filename = f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
#             wf = wave.open(raw_filename, 'wb')
#             wf.setnchannels(CHANNELS)
#             wf.setsampwidth(audio.get_sample_size(FORMAT))
#             wf.setframerate(RATE)
#             wf.writeframes(b''.join(frames))
#             wf.close()
            
#             preprocess_audio(raw_filename, processed_filename)

#             text = recognize_with_azure(processed_filename)
#             print("Recognized text:", text)
            

#     while recording:
#         if not audio_queue.empty():
#             data = audio_queue.get()
#             frames.append(data)

#             if is_silence(data):
#                 if silence_start is None:
#                     silence_start = time.time()
#                 elif time.time() - silence_start > SILENCE_DURATION:
#                     print("Silence detected, saving and recognizing")
#                     save_and_recognize()
#                     silence_start = None
#             else:
#                 silence_start = None

#     save_and_recognize()

# def index(request):
#     return render(request, 'index.html')

# @method_decorator(csrf_exempt, name='dispatch')
# class StartRecordingAPIView(View):
#     def post(self, request, *args, **kwargs):
#         global recording
#         if recording:
#             return JsonResponse({"error": "Recording is already in progress."}, status=400)

#         recording = True

#         record_thread = threading.Thread(target=continuous_recording)
#         silence_detect_thread = threading.Thread(target=detect_silence_and_recognize)

#         record_thread.start()
#         silence_detect_thread.start()

#         return JsonResponse({"message": "Recording started."}, status=200)

# @method_decorator(csrf_exempt, name='dispatch')
# class StopRecordingAPIView(View):
#     def post(self, request, *args, **kwargs):
#         global recording
#         if not recording:
#             return JsonResponse({"error": "Recording is not in progress."}, status=400)

#         recording = False
#         return JsonResponse({"message": "Recording stopped."}, status=200)
