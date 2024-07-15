# socketio_server/server.py

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
    response_data = ''
    sio.emit('audio_text', response_data, to=sid)

# Socket.IO 서버 실행
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)