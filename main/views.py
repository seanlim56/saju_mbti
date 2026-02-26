import json
import os
import random
import traceback
from datetime import date
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string  # HTML 렌더링용

# [수정 1] 라이브러리 미설치 시 서버 폭파(500 에러) 방지를 위해 try-except 적용
try:
    from korean_lunar_calendar import KoreanLunarCalendar
except ImportError:
    KoreanLunarCalendar = None

from . import saju_logic, text_bank
from .models import SajuResult
from .fortunes import get_today_fortune


# [중요] recommendations 모듈 로드
try:
    from .recommendations import get_location_recommendation, get_lucky_features
except ImportError:
    # 비상용 더미 함수
    def get_location_recommendation(e, seed_key=None):
        return {'direction': '동쪽', 'spot': '근처 공원', 'desc': '가볍게 산책하세요.', 'mission': '하늘 보기', 'avoid': '지하실', 'vibe': '편안함'}
    def get_lucky_features(e, seed_key=None):
        return {'color': 'Red', 'item': 'Ring', 'food': 'Apple', 'number': '7'}

# 오행 정규화 함수
def normalizeelement(elem):
    return {'목':'목', '화':'화', '토':'토', '금':'금', '수':'수'}.get(str(elem).strip(), '토')


def index(request):
    return render(request, 'main/index.html')


def result(request):
    if request.method != 'POST':
        return redirect('index')

    try:
        # 1. 입력 파싱
        name = request.POST.get('name')
        gender = request.POST.get('gender', 'male')
        birth_date = request.POST.get('birth_date')
        birth_time = request.POST.get('birth_time')
        mbti = request.POST.get('mbti', '').upper().strip()
        calendar_type = request.POST.get('calendar_type', 'solar')

        if not mbti or len(mbti) != 4:
            return render(request, 'main/index.html', {'error': 'MBTI를 올바르게 선택해주세요. (예: ENFP)'})

        if not birth_date:
            return render(request, 'main/index.html', {'error': '생년월일을 입력해주세요.'})

        try:
            year, month, day = map(int, birth_date.split('-'))
        except ValueError:
            return render(request, 'main/index.html', {'error': '날짜 형식이 올바르지 않습니다.'})

        # 음력 변환
        if calendar_type in ['lunar', 'lunar_leap']:
            if KoreanLunarCalendar is None:
                return render(request, 'main/index.html', {'error': '음력 변환 기능이 서버에 설치되어 있지 않습니다.'})
            calendar = KoreanLunarCalendar()
            try:
                is_leap = (calendar_type == 'lunar_leap')
                calendar.setLunarDate(year, month, day, is_leap)
                year = calendar.solarYear
                month = calendar.solarMonth
                day = calendar.solarDay
            except Exception:
                return render(request, 'main/index.html', {'error': '유효하지 않은 음력 날짜입니다.'})

        # 시간/분 정밀 파싱
        hour = None
        minute = 0
        if birth_time:
            try:
                parts = birth_time.split(':')
                hour = int(parts[0])
                if len(parts) > 1:
                    minute = int(parts[1])
            except ValueError:
                hour = None
                minute = 0

        # 2. 사주 분석
        saju_result = saju_logic.analyze_saju(
            year, month, day, 
            hour=hour, minute=minute, 
            gender=gender, 
            calendar_type='solar'
        )
        
        if not saju_result:
            return render(request, 'main/index.html', {'error': '사주 분석 실패'})

        main_god = saju_result.get('strongest_10', '비견')
        sub_god = saju_result.get('sub_10')
        weakest_five = saju_result.get('weakest_5', '비겁')
        strongest_element = saju_result.get('strongest', '목')
        weakest_element = saju_result.get('weakest_element')

        if not weakest_element:
            WEAK_BY_STRONG = {'목': '금', '화': '수', '토': '목', '금': '화', '수': '토'}
            weakest_element = WEAK_BY_STRONG.get(strongest_element, '토')

        element_counts = saju_result.get('counts', {'목':0, '화':0, '토':0, '금':0, '수':0})
        
        # [KEY] 무기 정보 가져오기
        weapons_list = saju_result.get('weapons', [])

        # 3. 텍스트 생성
        hidden_god = saju_result.get('hidden_10') 
        
        rich_texts = text_bank.get_rich_text(
            mbti=mbti, main_god=main_god, sub_god=sub_god,
            weakest_five=weakest_five, strongest_element=strongest_element,
            hidden_god=hidden_god,
            weakest_element=weakest_element,
            element_counts=element_counts
        )

        # 4. 보조 데이터 생성 (시드 적용으로 고정된 결과 생성)
        seed_key = f"{name}{year}{month}{day}{mbti}"

        today_fortune = get_today_fortune(
            user_year=year, user_month=month, user_day=day,
            strongest_10=main_god, sub_10=sub_god, mbti=mbti, strongest_element=strongest_element
        )

        norm_weakest = normalizeelement(weakest_element)
        
        location_info = get_location_recommendation(norm_weakest, seed_key=seed_key)
        lucky_info = get_lucky_features(norm_weakest, seed_key=seed_key)

        scores_json = json.dumps(saju_result.get('scores', {}), ensure_ascii=False)
        scores_10_json = json.dumps(saju_result.get('scores_10', {}), ensure_ascii=False)

        # 5. 세션에 임시 저장
        request.session['temp_result'] = {
            'name': name, 'year': year, 'month': month, 'day': day, 'hour': hour,
            'mbti': mbti, 'gender': gender,
            'strongest': main_god,
            'sub_10': sub_god,         # [FIX] 서브 십신 세션 저장
            'weakest_group': weakest_five,
            'scores_5': saju_result.get('scores', {}),
            'scores_10': saju_result.get('scores_10', {}),
            'element_counts': element_counts,
            'headline': rich_texts.get('headline', ''),
            'identity_core': rich_texts.get('identity_core', ''),
            'hidden_engine': rich_texts.get('hidden_engine', ''),
            'management_gap': rich_texts.get('management_gap', ''),
            'money': rich_texts.get('money', ''),
            'love': rich_texts.get('love', ''),
            'job': rich_texts.get('job', ''),
            'housing': rich_texts.get('housing', ''),
            'safety_line': rich_texts.get('safety_line', ''),
            'today_actions': rich_texts.get('today_actions', ''),
            'lucky_info': lucky_info,
            'location_info': location_info,
            'today_fortune': today_fortune,
            'weapons': weapons_list
        }

        # 6. 컨텍스트 전달
        context = request.session['temp_result'].copy()
        context['saju'] = saju_result.get('saju', {})
        context['scores_json'] = scores_json
        context['scores_10_json'] = scores_10_json
        context['weapons'] = weapons_list

        # [FIX] 오행 차트 widthratio용 분해 변수 (한글 키 접근 불안정 문제 해결)
        context['ec_mok']  = element_counts.get('목', 0)
        context['ec_hwa']  = element_counts.get('화', 0)
        context['ec_to']   = element_counts.get('토', 0)
        context['ec_geum'] = element_counts.get('금', 0)
        context['ec_su']   = element_counts.get('수', 0)

        return render(request, 'main/index.html', context)

    except Exception as e:
        print(traceback.format_exc())
        return render(request, 'main/index.html', {'error': f'오류 발생: {str(e)}'})


@login_required(login_url='login')
def save_result(request):
    """결과를 DB에 영구 저장"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '잘못된 접근입니다.'})
    
    temp = request.session.get('temp_result')
    if not temp:
        return JsonResponse({'success': False, 'message': '저장할 결과가 만료되었습니다. 다시 분석해주세요.'})

    try:
        SajuResult.objects.create(
            user=request.user,
            name=temp['name'],
            year=temp['year'], month=temp['month'], day=temp['day'], hour=temp.get('hour'),
            mbti=temp['mbti'], gender=temp.get('gender', 'male'),
            strongest=temp['strongest'],
            sub_10=temp.get('sub_10'),        # [FIX] 서브 십신 DB 저장
            weakest_group=temp['weakest_group'],
            scores_5=temp['scores_5'], scores_10=temp['scores_10'], element_counts=temp['element_counts'],
            headline=temp['headline'],
            identity_core=temp['identity_core'],
            hidden_engine=temp['hidden_engine'],
            management_gap=temp['management_gap'],
            money=temp['money'],
            love=temp['love'],
            job=temp['job'],
            housing=temp['housing'],
            safety_line=temp['safety_line'],
            today_actions=temp['today_actions'],
            lucky_info=temp['lucky_info'],
            location_info=temp['location_info'],
            today_fortune=temp['today_fortune'],
            weapons=temp.get('weapons', []) 
        )
        
        # [수정 2] 무한 중복 저장 방지: 저장이 끝나면 세션에서 결과 삭제
        if 'temp_result' in request.session:
            del request.session['temp_result']
            
        return JsonResponse({'success': True, 'message': '✅ 기록이 안전하게 저장되었습니다!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'저장 실패: {str(e)}'})


@login_required(login_url='login')
def result_detail(request, result_id):
    """저장된 결과 상세 보기 (데이터 누락 자동 복구 기능 포함)"""
    result = get_object_or_404(SajuResult, id=result_id, user=request.user)

    data_missing = (
        not result.location_info or 
        not result.location_info.get('spot') or
        not result.management_gap or
        not result.weapons
    )

    if data_missing:
        # [수정 3] strongest는 '십성'이므로, element_counts에서 가장 강한 '오행'을 찾음
        counts = result.element_counts or {}
        strong_elem = max(counts, key=counts.get) if counts else '토'
        
        weak_map = {'목':'금', '화':'수', '토':'목', '금':'화', '수':'토'}
        weakest = weak_map.get(strong_elem, '토')
        norm_weakest = normalizeelement(weakest)
        
        seed_key = f"{result.name}{result.year}{result.month}{result.day}{result.mbti}"

        if not result.location_info or not result.location_info.get('spot'):
            result.location_info = get_location_recommendation(norm_weakest, seed_key=seed_key)
            result.lucky_info = get_lucky_features(norm_weakest, seed_key=seed_key)
        
        if not result.management_gap:
            new_texts = text_bank.get_rich_text(
                mbti=result.mbti,
                main_god=result.strongest,
                sub_god=result.sub_10,           # [FIX] 서브 십신 추가
                weakest_five=result.weakest_group,  # [FIX] 약한 오행 그룹 추가
                strongest_element=strong_elem,
                weakest_element=weakest,
                element_counts=counts            # [FIX] 오행 카운트 추가
            )
            if not result.management_gap: result.management_gap = new_texts.get('management_gap', '')
            if not result.safety_line: result.safety_line = new_texts.get('safety_line', '')
            if not result.hidden_engine: result.hidden_engine = new_texts.get('hidden_engine', '')

        if not result.weapons:
            saju_res = saju_logic.analyze_saju(
                result.year, result.month, result.day, 
                hour=result.hour, minute=0, 
                gender=result.gender
            )
            if saju_res and 'weapons' in saju_res:
                result.weapons = saju_res['weapons']
            
        result.save()

    return render(request, 'main/result_detail.html', {'result': result})


def signup(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(); login(request, user); return redirect('index')
    else: form = UserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user(); login(request, user); return redirect(request.GET.get('next', 'index'))
    else: form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request); return redirect('index')

# [기능 추가] 가장 최근 분석 결과를 가져와 대시보드 데이터로 렌더링
@login_required(login_url='login')
def mypage(request):
    results = SajuResult.objects.filter(user=request.user).order_by('-created_at')
    
    # 🌟 가장 최근 저장한 결과를 '메인 프로필'로 간주
    main_profile = results.first()
    today_dash = None
    
    if main_profile:
        # 오늘 날짜 기준 운세 생성 - element_counts에서 가장 강한 오행 추출
        counts = main_profile.element_counts or {}
        strong_elem_for_dash = max(counts, key=counts.get) if counts else None
        today_dash = get_today_fortune(
            user_year=main_profile.year,
            user_month=main_profile.month,
            user_day=main_profile.day,
            strongest_10=main_profile.strongest,
            sub_10=main_profile.sub_10,
            mbti=main_profile.mbti,
            strongest_element=strong_elem_for_dash  # [FIX] result 페이지와 일관된 시드값 보장
        )

    return render(request, 'main/mypage.html', {
        'results': results,
        'main_profile': main_profile,
        'today_dash': today_dash
    })