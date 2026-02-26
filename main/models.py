from django.db import models
from django.contrib.auth.models import User

class SajuResult(models.Model):
    MBTI_CHOICES = [
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('INFJ', 'INFJ'), ('INTJ', 'INTJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('INFP', 'INFP'), ('INTP', 'INTP'),
        ('ESTP', 'ESTP'), ('ESFP', 'ESFP'), ('ENFP', 'ENFP'), ('ENTP', 'ENTP'),
        ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'), ('ENFJ', 'ENFJ'), ('ENTJ', 'ENTJ'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 1. 기본 입력 정보
    name = models.CharField(max_length=50, default="이름없음")
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    hour = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, default='male')
    mbti = models.CharField(max_length=10, choices=MBTI_CHOICES)

    # 2. 분석 핵심 결과
    strongest = models.CharField(max_length=20)
    sub_10 = models.CharField(max_length=20, null=True, blank=True)   # [FIX] 서브 십신 저장
    weakest_group = models.CharField(max_length=20, null=True, blank=True)
    
    # 3. 점수 및 그래프 데이터 (JSON)
    scores_5 = models.JSONField(default=dict, blank=True)
    scores_10 = models.JSONField(default=dict, blank=True)
    element_counts = models.JSONField(default=dict, blank=True)

    # 4. 상세 텍스트 저장
    headline = models.CharField(max_length=200, blank=True)
    identity_core = models.TextField(blank=True)
    
    # 분석 핵심 3종 세트
    hidden_engine = models.TextField(blank=True)   # 숨겨진 본능
    management_gap = models.TextField(blank=True)  # 관리해야 할 갭
    safety_line = models.TextField(blank=True)     # 안전 가이드

    money = models.TextField(blank=True)
    love = models.TextField(blank=True)
    job = models.TextField(blank=True)
    housing = models.TextField(blank=True)
    today_actions = models.TextField(blank=True)
    
    # 5. 부가 정보 (운세, 추천, 무기)
    lucky_info = models.JSONField(default=dict, blank=True)
    location_info = models.JSONField(default=dict, blank=True)
    today_fortune = models.JSONField(default=dict, blank=True)
    
    # [CRITICAL UPDATE] Hidden Weapons (특수살) 저장용 필드 추가
    weapons = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.user.username}] {self.name} - {self.created_at.strftime('%Y-%m-%d')}"