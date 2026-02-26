from django.contrib import admin
from django.urls import path, include # include 추가됨

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), # 메인 앱의 주소들을 포함시켜라
]