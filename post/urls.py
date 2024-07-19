from django.urls import path
from .views      import *
from django.conf.urls.static import static
from config import settings

urlpatterns = [
   # path('signup/', .as_view()), # 
   path('send/',send ), # 
   path('postlist/', PostList.as_view()), # 전체 공지사항 가져오기
   path('postdetail/<int:pk>/', PostDetailView.as_view()), # 공지사항 하나 가져오기
   path('postcreate/', PostCreateView.as_view()), # 공지사항 생성
   path('postedit/<int:pk>/', PostEditView.as_view()), # 공지사항 수정
   path('postdelete/<int:pk>/', PostDeleteView.as_view()), # 공지사항 삭제
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)