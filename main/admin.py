from django.contrib import admin
from .models import SajuResult

# 이렇게 데코레이터를 쓰면 관리자 페이지를 내 입맛대로 꾸밀 수 있습니다.
@admin.register(SajuResult)
class SajuResultAdmin(admin.ModelAdmin):
    # 1. 목록 화면에서 바로 보여줄 항목들 (사용자, 생년월일, MBTI, 결과, 저장일시)
    list_display = ('user', 'year', 'month', 'day', 'mbti', 'strongest', 'created_at')
    
    # 2. 오른쪽에 필터(거름망) 만들기 (MBTI별, 강한 기운별로 모아보기 가능)
    list_filter = ('mbti', 'strongest')
    
    # 3. 검색창 만들기 (사용자 이름이나 MBTI로 검색 가능)
    search_fields = ('user__username', 'mbti', 'strongest')
    
    # 4. 최신순으로 정렬해서 보여주기
    ordering = ('-created_at',)