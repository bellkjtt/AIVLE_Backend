# import socketio
# import eventlet
# import os
# from datetime import datetime
# import requests

# # Socket.IO 서버 인스턴스 생성 및 모든 도메인에서의 CORS 허용
# sio = socketio.Server(cors_allowed_origins='*')
# # WSGI 애플리케이션 생성
# app = socketio.WSGIApp(sio)

# # 파일 업로드 폴더 생성
# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # 클라이언트가 연결될 때 실행되는 이벤트
# @sio.event
# def connect(sid, environ):
#     print("연결됨", sid)

# # 클라이언트 연결이 끊길 때 실행되는 이벤트
# @sio.event
# def disconnect(sid):
#     print("연결 끊김", sid)

# # 클라이언트로부터 오디오 데이터 수신 시 실행되는 이벤트
# @sio.event
# def audio_data(sid, data):
#     print("파일 전송됨")
    
#     # 현재 시간으로 파일 이름 생성
#     filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.wav'
#     file_path = os.path.join(UPLOAD_FOLDER, filename)
    
#     # 파일 저장
#     with open(file_path, 'wb') as f:
#         f.write(data)
#     print("파일 저장 완료:", file_path)
    
#     # 장고 STT 뷰 호출
#     with open(file_path, 'rb') as fp:
#         files = {'audio': fp}
#         print("view 호출")
#         try:
#             response = requests.post('http://127.0.0.1:8000/stt/process_audio/', files=files)
#         except Exception as e:
#             print("Django 뷰 호출 중 예외 발생:", str(e))
#             sio.emit('audio_text', 'Django 뷰 호출 실패', to=sid)
#             return
    
#         print(response.status_code)
#         print(response.json())
        
#         if response.status_code == 200:
#             response_data = response.json()
#             recognized_text = response_data.get('message', 'No text recognized')
#             message = f"{recognized_text}"
            
#             # # 경도와 위도 정보 추출 (예시)
#             latitude = response_data.get('latitude', 0)
#             longitude = response_data.get('longitude', 0)
            
#             # report에 audio_text 전송
           
            
#             # report3에 위치 정보 전송
#             location_data = {
#                 'latitude': latitude,
#                 'longitude': longitude,
#                 'text': recognized_text
#             }
#             sio.emit('report3', location_data, to=sid)
#         else:
#             message = 'Django 뷰 호출 실패'
#             sio.emit('audio_text', message, to=sid)

#     # print("응답 데이터:", message)

# # Socket.IO 서버 실행
# if __name__ == '__main__':
#     eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
    
    
    
import socketio
import eventlet
import os
from datetime import datetime
import requests

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 모든 위치 데이터를 저장할 리스트
all_locations = []

@sio.event
def connect(sid, environ):
    print("연결됨", sid)

@sio.event
def disconnect(sid):
    print("연결 끊김", sid)

@sio.event
def audio_data(sid, data):
    print("파일 전송됨")
    
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.wav'
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(data)
    print("파일 저장 완료:", file_path)
    
    with open(file_path, 'rb') as fp:
        files = {'audio': fp}
        print("view 호출")
        try:
            response = requests.post('http://127.0.0.1:8000/stt/process_audio/', files=files)
        except Exception as e:
            print("Django 뷰 호출 중 예외 발생:", str(e))
            return
    
        print(response.status_code)
        print(response.json())
        
        if response.status_code == 200:
            response_data = response.json()
            recognized_text = response_data.get('message', 'No text recognized')
            log_id = response_data.get('log_id', None)
            latitude = response_data.get('latitude', 0)
            longtitue = response_data.get('longtitue', 0)
            place = response_data.get('place', None)
            
            if recognized_text!=None:
                sio.emit('audio_text', {
                    'message': recognized_text,
                    'log_id': log_id
                }, to=sid)
            
            if latitude !=0 or longtitue!=0:
                # 새 위치 정보를 리스트에 추가
                all_locations.append({
                    'lat': latitude,
                    'lng': longtitue,
                    'name': 'New Report',
                    'place': place,
                    'description': recognized_text
                })
        else:
            message = 'Django 뷰 호출 실패'
            sio.emit('audio_text', {'message': message}, to=sid)
            print('Django 뷰 호출 실패')
@sio.event
def request_initial_locations(sid):
    sio.emit('locations_update', all_locations, to=sid)

@sio.event
def request_locations(sid):
    sio.emit('locations_update', all_locations, to=sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)