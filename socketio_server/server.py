import socketio
import eventlet
import os
import wave
import pyaudio
import threading
import time
import queue
from datetime import datetime
import requests
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
SILENCE_DURATION = 2  # 무음이 일정 시간 이상 지속되면 (초)

# PyAudio 초기화
audio = pyaudio.PyAudio()

# 오디오 큐 초기화
audio_queue = queue.Queue()

# 전역 변수
recording = False
silence_start = None

# Socket.IO 서버 인스턴스 생성 및 모든 도메인에서의 CORS 허용
sio = socketio.Server(cors_allowed_origins='*')
# WSGI 애플리케이션 생성
app = socketio.WSGIApp(sio)

# 파일 업로드 폴더 생성
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def recognize_speech(file_path):
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    with open(file_path, 'rb') as data:
        response = requests.post(url, data=data, headers=headers)
    rescode = response.status_code
    if rescode == 200:
        return response.json().get('text', 'No text recognized')
    else:
        return f"Error: {response.text}"

def continuous_recording():
    global recording
    wf_full = wave.open(f"full_conversation_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav", 'wb')
    wf_full.setnchannels(CHANNELS)
    wf_full.setsampwidth(audio.get_sample_size(FORMAT))
    wf_full.setframerate(RATE)

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")
    while recording:
        data = stream.read(CHUNK)
        audio_queue.put(data)
        wf_full.writeframes(data)

    stream.stop_stream()
    stream.close()
    wf_full.close()

def detect_silence_and_recognize():
    global recording, silence_start
    frames = []

    def is_silence(data):
        return np.max(np.frombuffer(data, dtype=np.int16)) < SILENCE_THRESHOLD

    def save_and_recognize():
        nonlocal frames
        filename = f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        frames = []

        recognized_text = recognize_speech(filename)
        sio.emit('audio_text', recognized_text)

    while recording:
        if not audio_queue.empty():
            data = audio_queue.get()
            frames.append(data)

            if is_silence(data):
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    save_and_recognize()
                    silence_start = None
            else:
                silence_start = None

    if frames:
        save_and_recognize()

# 클라이언트가 연결될 때 실행되는 이벤트
@sio.event
def connect(sid, environ):
    print("연결됨", sid)
    start_recording(sid)  # 연결되면 녹음을 자동으로 시작

# 클라이언트 연결이 끊길 때 실행되는 이벤트
@sio.event
def disconnect(sid):
    print("연결 끊김", sid)
    stop_recording(sid)  # 연결이 끊기면 녹음을 중지

# 클라이언트로부터 녹음 시작 신호 수신 시 실행되는 이벤트
def start_recording(sid):
    global recording
    if recording:
        sio.emit('error', 'Recording is already in progress.', to=sid)
        return

    recording = True
    record_thread = threading.Thread(target=continuous_recording)
    detect_silence_thread = threading.Thread(target=detect_silence_and_recognize)

    record_thread.start()
    detect_silence_thread.start()

    sio.emit('status', 'Recording started.', to=sid)

# 클라이언트로부터 녹음 중지 신호 수신 시 실행되는 이벤트
@sio.event
def stop_recording(sid):
    global recording
    if not recording:
        sio.emit('error', 'Recording is not in progress.', to=sid)
        return

    recording = False
    sio.emit('status', 'Recording stopped.', to=sid)

# Socket.IO 서버 실행
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
