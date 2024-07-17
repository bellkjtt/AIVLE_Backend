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
from modules.gpt_text_processor import GPTProcessor

# 네이버 클로바 스피치 API 설정
client_id = "etu7ckegx5"
client_secret = "4WtVsc9mDlMZJmsrswHcZIaOlW2Fz200DMAmEFvO"
lang = "Kor"  # 언어 코드 (한국어: Kor)
url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang

# 오디오 설정
CHUNK = 4096  # 버퍼 크기를 증가
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500  # 무음 감지 임계값
SILENCE_DURATION = 5  # 무음이 일정 시간 이상 지속되면 (초)
MIN_SOUND_DURATION = 1.0  # 최소 음성 데이터 길이 (초)
WAVE_OUTPUT_FILENAME = "output.wav"
FULL_CONVERSATION_FILENAME = "full_conversation.wav"

# PyAudio 초기화
audio = pyaudio.PyAudio()

# 오디오 큐 초기화
audio_queue = queue.Queue()

# 전역 변수
recording = False
silence_start = None
text = ''
lock = threading.Lock()

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
        if text != '':
            print("Recognized text:", text)
            processor = GPTProcessor()
            result = processor.text_preprocessor(text)
            print(result)
    else:
        print("Error:", response.text)

# 전체 녹음 저장
def continuous_recording():
    global recording
    wf_full = wave.open(FULL_CONVERSATION_FILENAME, 'wb')
    wf_full.setnchannels(CHANNELS)
    wf_full.setsampwidth(audio.get_sample_size(FORMAT))
    wf_full.setframerate(RATE)

    # 큐에 오디오 넣기
    def callback(in_data, frame_count, time_info, status):
        if not recording:
            return in_data, pyaudio.paComplete
        wf_full.writeframes(in_data)
        audio_queue.put(in_data)
        return in_data, pyaudio.paContinue

    # 녹음 시작
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
    # 녹음 끝
    stream.stop_stream()
    stream.close()
    wf_full.close()
    print("Recording stopped")

# 무음 감지 후 recognize
def detect_silence_and_recognize():
    global recording, silence_start
    frames = []
    sound_start = None

    # 무음 감지
    def is_silence(data):
        return np.max(np.frombuffer(data, dtype=np.int16)) < SILENCE_THRESHOLD

    # 녹음된 음성이 존재하면 output.wav로 저장 후 recognize_speech 함수 실행
    def save_and_recognize():
        nonlocal frames, sound_start
        if frames and sound_start:
            duration = time.time() - sound_start
            if duration >= MIN_SOUND_DURATION:
                filename = "output.wav"
                wf = wave.open(filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                frames = []

                recognize_speech(filename)
            else:
                print("Recording too short, not sending to STT API")
            sound_start = None

    while recording:
        if not audio_queue.empty():
            data = audio_queue.get()
            frames.append(data)

            # 무음 감지시 save_and_recognize 함수 실행
            if is_silence(data):
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    print("Silence detected, saving and recognizing")
                    save_and_recognize()
                    silence_start = None
            else:
                if sound_start is None:
                    sound_start = time.time()
                silence_start = None

    save_and_recognize()

def index(request):
    return render(request, 'index.html')

# 녹음 시작 버튼을 누르면 멀티스레드를 활용해 녹음 시작
@method_decorator(csrf_exempt, name='dispatch')
class StartRecordingAPIView(View):
    def post(self, request, *args, **kwargs):
        global recording
        with lock:
            if recording:
                return JsonResponse({"error": "Recording is already in progress."}, status=400)

            recording = True

            record_thread = threading.Thread(target=continuous_recording)
            silence_detect_thread = threading.Thread(target=detect_silence_and_recognize)

            record_thread.start()
            silence_detect_thread.start()

        return JsonResponse({"message": "Recording started."}, status=200)

# 녹음 끝
@method_decorator(csrf_exempt, name='dispatch')
class StopRecordingAPIView(View):
    def post(self, request, *args, **kwargs):
        global recording
        with lock:
            if not recording:
                return JsonResponse({"error": "Recording is not in progress."}, status=400)

            recording = False

        return JsonResponse({"message": "Recording stopped."}, status=200)
