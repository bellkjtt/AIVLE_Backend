import socketio
import eventlet
import os
from datetime import datetime
import requests

# Socket.IO 서버 인스턴스 생성 및 모든 도메인에서의 CORS 허용
sio = socketio.Server(cors_allowed_origins='*')
# WSGI 애플리케이션 생성
app = socketio.WSGIApp(sio)

# 파일 업로드 폴더 생성
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 클라이언트가 연결될 때 실행되는 이벤트
@sio.event
def connect(sid, environ):
    print("연결됨", sid)

# 클라이언트 연결이 끊길 때 실행되는 이벤트
@sio.event
def disconnect(sid):
    print("연결 끊김", sid)

# 클라이언트로부터 오디오 데이터 수신 시 실행되는 이벤트
@sio.event
def audio_data(sid, data):
    print("파일 전송됨")
    
    # 현재 시간으로 파일 이름 생성
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.wav'
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # 파일 저장
    with open(file_path, 'wb') as f:
        f.write(data)
    print("파일 저장 완료:", file_path)

    # 장고 STT 뷰 호출
    with open(file_path, 'rb') as fp:
        files = {'audio': fp}
        print("view 호출")
        try:
            response = requests.post('http://127.0.0.1:8000/stt/process_audio/', files=files)
        except Exception as e:
            print("Django 뷰 호출 중 예외 발생:", str(e))
            sio.emit('audio_text', 'Django 뷰 호출 실패', to=sid)
            return

    print(response.content)

    if response.status_code == 200:
        response_data = response.json()
        recognized_text = response_data.get('full_text', 'No text recognized')
        message = f"Transcription: {recognized_text}"
    else:
        message = 'Django 뷰 호출 실패'

    print("응답 데이터:", message)
    sio.emit('audio_text', message, to=sid)

# Socket.IO 서버 실행
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
