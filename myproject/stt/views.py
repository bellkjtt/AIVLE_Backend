import os
import json
import base64
import wave
import pyaudio
import threading
import queue
import urllib3
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# 설정
CHUNK = 1024  # 버퍼 크기
FORMAT = pyaudio.paInt16  # 음성 포맷
CHANNELS = 1  # 모노 채널
RATE = 16000  # 샘플링 레이트
RECORD_SECONDS = 1  # 녹음 시간 단위 (1초)
WAVE_OUTPUT_FILENAME = "output.wav"  # 전체 저장할 파일 이름

# ETRI API 설정
openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
accessKey = "2b233e5f-a9c9-4224-989a-5b3d781f3385"
languageCode = "korean"

# 전역 변수
recording = False
audio_queue = queue.Queue()
frames = []

def recognize_with_etri(audio_data):
    audio_contents = base64.b64encode(audio_data).decode("utf8")
    
    request_json = {
        "argument": {
            "language_code": languageCode,
            "audio": audio_contents
        }
    }
    
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
        body=json.dumps(request_json)
    )
    
    response_data = json.loads(response.data.decode("utf-8"))
    return response_data

def index(request):
    return render(request, 'index.html')

def start_recording(request):
    global recording
    if request.method == "POST":
        if recording:
            return JsonResponse({"error": "Recording is already in progress."}, status=400)
        
        recording = True
        
        def audio_recorder():
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            
            print("Recording...")
            try:
                while recording:
                    audio_data = []
                    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                        data = stream.read(CHUNK)
                        audio_data.append(data)
                    
                    audio_data = b''.join(audio_data)
                    frames.append(audio_data)
                    audio_queue.put(audio_data)
            except Exception as e:
                print("Recording error:", e)
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                audio_queue.put(None)
        
        def process_audio():
            while True:
                audio_data = audio_queue.get()
                if audio_data is None:
                    break
                
                response = recognize_with_etri(audio_data)
                if response.get('result') == 0:
                    text = response['return_object']['recognized']
                    print("Recognized text: ", text)
                else:
                    print("Error recognizing audio with ETRI API")
        
        recording_thread = threading.Thread(target=audio_recorder)
        processing_thread = threading.Thread(target=process_audio)
        
        recording_thread.start()
        processing_thread.start()
        
        recording_thread.join()
        processing_thread.join()
        
        return JsonResponse({"message": "Recording started."})
    
    return JsonResponse({"error": "Invalid request method."}, status=400)

def stop_recording(request):
    global recording
    if request.method == "POST":
        if not recording:
            return JsonResponse({"error": "Recording is not in progress."}, status=400)
        
        recording = False
        
        # 전체 녹음 데이터 저장
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        return JsonResponse({"message": "Recording stopped and saved as " + WAVE_OUTPUT_FILENAME})
    
    return JsonResponse({"error": "Invalid request method."}, status=400)
