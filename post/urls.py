from django.urls import path
from .views      import *
from django.conf.urls.static import static
from config import settings
from .views import LogDetailView
urlpatterns = [
   # path('signup/', .as_view()), # 
   path('send/',send ), # 
   path('postlist/', PostList.as_view()), # 전체 공지사항 가져오기
   path('postdetail/<int:pk>/', PostDetailView.as_view()), # 공지사항 하나 가져오기
   path('postcreate/', PostCreateView.as_view()), # 공지사항 생성
   path('postedit/<int:pk>/', PostEditView.as_view()), # 공지사항 수정
   path('postdelete/<int:pk>/', PostDeleteView.as_view()), # 공지사항 삭제
   path('postlog/', PostDataView.as_view()), # 신고 내역 로그 확인
   path('postlog/<int:pk>/', PostLogView.as_view()),
   path('categorycount/', Disaster.as_view()), # 신고 내역 종류 별 개수
   path('daylog/', DayLog.as_view()), # 날짜별 신고 내역
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)