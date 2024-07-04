# stt/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat_log, AudioFile
from .views import voice_stt #STT 함수 가져오기


# 웹 소켓 소비자 클래스 정의
class STTConsumer(AsyncJsonWebsocketConsumer):
    
    # 웹소켓 연결 처리
    async def connect(self):
        await self.accept()

    # 웹소켓 연결 종료 처리
    async def disconnect(self, close_code):
        pass

    # JSON 메시지 수신 처리
    async def receive_json(self, content):
        audio_id = content.get('audio_id') # 수신한 메시지에서 'audio_id'를 가져옴
        if not audio_id:
            await self.send_json({"error": "No audio_id provided"})
            return
        
        # 데이터베이스에서 audio_id에 해당하는 AudioFile 객체를 가져옴
        audio_file = await database_sync_to_async(AudioFile.objects.get)(id=audio_id)
        
        # STT 함수 실행
        transcription = voice_stt(audio_file.file)
        
        # TEXT JSON 형식으로 전송
        await self.send_json({
            transcription
        })
