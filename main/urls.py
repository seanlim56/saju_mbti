from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('save/', views.save_result, name='save_result'),          # [추가됨] 저장
    path('mypage/', views.mypage, name='mypage'),
    path('detail/<int:result_id>/', views.result_detail, name='result_detail'), # [추가됨] 상세
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
