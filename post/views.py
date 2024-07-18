from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.serializers import serialize
from django.views import View
from django.http import JsonResponse
from .models import Post
import json, base64
from config.decorators import verify_jwt_token
from .forms import FileUploadForm

# 이미지 읽기
def get_base64_image(image_field):
    if not image_field:
        return None
    with image_field.open('rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f'data:{image_field.file.content_type};base64,{encoded_string}'

# 전체 공지사항 가져오기
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_jwt_token, name='dispatch')
class PostList(View):
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        posts_json = serialize('json', posts)
        return JsonResponse(json.loads(posts_json), safe=False, status=200)

# 하나씩 공지사항 가져오기
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_jwt_token, name='dispatch')
class PostDetailView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post_json = serialize('json', [post])[1:-1]
        post_data = json.loads(post_json)
        post_data['fields']['file'] = get_base64_image(post.file)
        return JsonResponse(post_data, safe=False)
    
# 공지사항 작성
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_jwt_token, name='dispatch')
class PostCreateView(View):
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        form = FileUploadForm(body_data, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            post_json = serialize('json', [post])[1:-1]
            post_data = json.loads(post_json)
            post_data['fields']['file'] = get_base64_image(post.file)
            return JsonResponse(post_data, safe=False, status=200)
        return JsonResponse(form.errors, status=400)

# 공지사항 수정
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_jwt_token, name='dispatch')
class PostEditView(View):
    def post(self, request, pk):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        post = get_object_or_404(Post, pk=pk)
        form = FileUploadForm(body_data, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            post_json = serialize('json', [post])[1:-1]
            post_data = json.loads(post_json)
            post_data['fields']['file'] = get_base64_image(post.file)
            return JsonResponse(post_data, safe=False, status=200)
        return JsonResponse(form.errors, status=400)

# 공지사항 삭제
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(verify_jwt_token, name='dispatch')
class PostDeleteView(View):
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return JsonResponse({'status': 'success'}, status=200)
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from stt.models import EmergencyCalls
from django.core.serializers import serialize
import json
# import socketio

# Socket.IO 서버 인스턴스 생성
# sio = socketio.Server(cors_allowed_origins='*')

# 데이터 가져오기
def get_data():
    
    # 데이터 검색
    data = EmergencyCalls.objects.order_by('-date')
    
    # 데이터를 JSON 형식으로 직렬화
    json_data = serialize('json', data)
    
    # JSON 데이터를 Python 객체로 변환
    json_data = json.loads(json_data)
    
    return json_data

# 데이터 전송
def send(request):
    json_data = get_data()
    print(json_data)
    return JsonResponse(json_data, safe=False)


# # 클라이언트로부터 오디오 데이터 수신 시 실행되는 이벤트
# @sio.event
# def post_data(sid):

#     # 데이터 저장 후 데이터베이스에서 최신 데이터를 쿼리
#     json_data = get_data()

#     # 클라이언트에게 최신 데이터 전송
#     sio.emit('send', json_data, to=sid)