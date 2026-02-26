import datetime
from datetime import date, datetime as dt

# [NEW] 음력 변환 라이브러리
try:
    from korean_lunar_calendar import KoreanLunarCalendar
except ImportError:
    KoreanLunarCalendar = None


# ==========================================================
# 1. 기초 데이터
# ==========================================================

CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

JIJI_OHENG = {
    '자': '수', '축': '토', '인': '목', '묘': '목', '진': '토', '사': '화',
    '오': '화', '미': '토', '신': '금', '유': '금', '술': '토', '해': '수'
}

OHENG_MAP = {
    '갑': '목', '을': '목', '병': '화', '정': '화', '무': '토',
    '기': '토', '경': '금', '신': '금', '임': '수', '계': '수'
}

YIN_YANG = {
    '갑': True, '을': False, '병': True, '정': False, '무': True,
    '기': False, '경': True, '신': False, '임': True, '계': False
}

JIJANG_GAN = {
    '자': ['임', None, '계'], 
    '축': ['계', '신', '기'], 
    '인': ['무', '병', '갑'], 
    '묘': ['갑', None, '을'],
    '진': ['을', '계', '무'],
    '사': ['무', '경', '병'],
    '오': ['병', '기', '정'],
    '미': ['정', '을', '기'],
    '신': ['무', '임', '경'],
    '유': ['경', None, '신'],
    '술': ['신', '정', '무'],
    '해': ['무', '갑', '임']
}

TEN_DEITIES_5 = {
    '목': {'목': '비겁', '화': '식상', '토': '재성', '금': '관성', '수': '인성'},
    '화': {'목': '인성', '화': '비겁', '토': '식상', '금': '재성', '수': '관성'},
    '토': {'목': '관성', '화': '인성', '토': '비겁', '금': '식상', '수': '재성'},
    '금': {'목': '재성', '화': '관성', '토': '인성', '금': '비겁', '수': '식상'},
    '수': {'목': '식상', '화': '재성', '토': '관성', '금': '인성', '수': '비겁'}
}

TEN_GODS_MAP = {
    ('비겁', True): '비견', ('비겁', False): '겁재',
    ('식상', True): '식신', ('식상', False): '상관',
    ('재성', True): '편재', ('재성', False): '정재',
    ('관성', True): '편관', ('관성', False): '정관',
    ('인성', True): '편인', ('인성', False): '정인'
}

GAN_HAP_MONTH_START = { 0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0 }
GAN_HAP_HOUR_START = { 0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8 }

IPCHUN_TABLE = {
    1980: (2, 5, 0, 10), 1981: (2, 4, 6, 0), 1982: (2, 4, 11, 48), 1983: (2, 4, 17, 40),
    1984: (2, 4, 23, 29), 1985: (2, 4, 5, 12), 1986: (2, 4, 11, 8), 1987: (2, 4, 16, 52),
    1988: (2, 4, 22, 43), 1989: (2, 4, 4, 28), 1990: (2, 4, 10, 15), 1991: (2, 4, 16, 9),
    1992: (2, 4, 21, 54), 1993: (2, 4, 3, 43), 1994: (2, 4, 9, 31), 1995: (2, 4, 15, 24),
    1996: (2, 4, 21, 15), 1997: (2, 4, 3, 4), 1998: (2, 4, 8, 56), 1999: (2, 4, 14, 57),
    2000: (2, 4, 20, 40), 2001: (2, 4, 2, 28), 2002: (2, 4, 8, 24), 2003: (2, 4, 14, 5),
    2004: (2, 4, 19, 56), 2005: (2, 4, 1, 43), 2006: (2, 4, 7, 27), 2007: (2, 4, 13, 18),
    2008: (2, 4, 19, 0), 2009: (2, 4, 0, 50), 2010: (2, 4, 6, 48), 2011: (2, 4, 12, 33),
    2012: (2, 4, 18, 22), 2013: (2, 4, 0, 13), 2014: (2, 4, 6, 3), 2015: (2, 4, 11, 58),
    2016: (2, 4, 17, 46), 2017: (2, 3, 23, 34), 2018: (2, 4, 5, 28), 2019: (2, 4, 11, 14),
    2020: (2, 4, 17, 3), 2021: (2, 3, 22, 59), 2022: (2, 4, 4, 51), 2023: (2, 4, 10, 42),
    2024: (2, 4, 16, 27), 2025: (2, 3, 22, 10), 2026: (2, 4, 4, 2)
}


# ==========================================================
# 2. HELPER FUNCTIONS
# ==========================================================

def get_ipchun_time(year):
    return IPCHUN_TABLE.get(year, (2, 4, 12, 0))


def get_corrected_year(year, month, day, hour, minute):
    i_month, i_day, i_hour, i_min = get_ipchun_time(year)
    is_past = False
    if month > i_month: is_past = True
    elif month == i_month:
        if day > i_day: is_past = True
        elif day == i_day:
            if (hour > i_hour) or (hour == i_hour and minute >= i_min): is_past = True
    return year if is_past else year - 1


def get_gan_zhi_year(saju_year):
    return CHEONGAN[(saju_year - 4) % 10] + JIJI[(saju_year - 4) % 12]


def get_gan_zhi_month(saju_year, month, day):
    target_month = month
    if day < 6:
        target_month -= 1
        if target_month == 0: target_month = 12
    
    year_stem_idx = (saju_year - 4) % 10
    start_stem_idx = GAN_HAP_MONTH_START[year_stem_idx % 5]
    
    month_offset = target_month - 2
    if month_offset < 0: month_offset += 12
    
    month_stem_idx = (start_stem_idx + month_offset) % 10
    month_branch_idx = (2 + month_offset) % 12
    return CHEONGAN[month_stem_idx] + JIJI[month_branch_idx]


def get_gan_zhi_day(year, month, day):
    base = date(1900, 1, 1)
    target = date(year, month, day)
    diff = (target - base).days
    return CHEONGAN[(0 + diff) % 10] + JIJI[(10 + diff) % 12], CHEONGAN[(0 + diff) % 10], JIJI[(10 + diff) % 12]


def get_gan_zhi_hour(day_gan, hour, minute):
    time_val = hour + (minute / 60.0)
    if time_val >= 23.5 or time_val < 1.5: branch_idx = 0
    else: branch_idx = int((time_val - 1.5) // 2) + 1
    
    day_stem_idx = CHEONGAN.index(day_gan)
    start_hour_stem = GAN_HAP_HOUR_START[day_stem_idx % 5]
    return CHEONGAN[(start_hour_stem + branch_idx) % 10] + JIJI[branch_idx]


# ==========================================================
# 3. 분석 및 점수 계산
# ==========================================================

def calculate_scores(day_gan, saju_dict):
    my_element = OHENG_MAP[day_gan]
    my_yinyang = YIN_YANG[day_gan]
    
    scores_5 = {'비겁': 0, '식상': 0, '재성': 0, '관성': 0, '인성': 0}
    scores_10 = {k:0 for k in ['비견','겁재','식신','상관','편재','정재','편관','정관','편인','정인']}
    
    targets = []
    if saju_dict['year']: targets.extend([(saju_dict['year'][0], 10), (saju_dict['year'][1], 10)])
    if saju_dict['month']: targets.extend([(saju_dict['month'][0], 10), (saju_dict['month'][1], 30)])
    if saju_dict['day']: targets.extend([(saju_dict['day'][1], 15)])
    if 'hour' in saju_dict and saju_dict['hour']:
        targets.append((saju_dict['hour'][0], 10))
        targets.append((saju_dict['hour'][1], 10))
    
    for char, weight in targets:
        char_element = JIJI_OHENG.get(char, OHENG_MAP.get(char))
        if not char_element: continue

        relation_5 = TEN_DEITIES_5[my_element][char_element]
        
        target_yinyang = None
        if char in JIJI:
            idx = JIJI.index(char)
            target_yinyang = True if idx % 2 == 0 else False
        else:
            target_yinyang = YIN_YANG.get(char, True)
            
        is_same = (my_yinyang == target_yinyang)
        relation_10 = TEN_GODS_MAP.get((relation_5, is_same), '비견')
        
        scores_5[relation_5] += weight
        scores_10[relation_10] += weight
        
        if char in JIJI:
            hidden_stems = JIJANG_GAN.get(char, [])
            hidden_weight = weight * 0.3
            for h_stem in hidden_stems:
                if not h_stem: continue
                h_element = OHENG_MAP.get(h_stem)
                if not h_element: continue
                h_relation_5 = TEN_DEITIES_5[my_element][h_element]
                h_yinyang = YIN_YANG.get(h_stem, True)
                h_is_same = (my_yinyang == h_yinyang)
                h_relation_10 = TEN_GODS_MAP.get((h_relation_5, h_is_same), '비견')
                scores_5[h_relation_5] += int(hidden_weight)
                scores_10[h_relation_10] += int(hidden_weight)

    scores_5 = {k: int(v) for k,v in scores_5.items()}
    scores_10 = {k: int(v) for k,v in scores_10.items()}
    return scores_5, scores_10


def calculate_element_counts(saju_dict):
    counts = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
    text = saju_dict['year'] + saju_dict['month'] + saju_dict['day'] + saju_dict.get('hour', '')
    for char in text:
        elem = JIJI_OHENG.get(char, OHENG_MAP.get(char))
        if elem: counts[elem] += 1
    return counts


def get_weakest_group(scores_10):
    groups = {'비겁':0, '식상':0, '재성':0, '관성':0, '인성':0}
    mapping = {
        '비견':'비겁', '겁재':'비겁', '식신':'식상', '상관':'식상',
        '편재':'재성', '정재':'재성', '편관':'관성', '정관':'관성',
        '편인':'인성', '정인':'인성'
    }
    for k, v in scores_10.items():
        groups[mapping[k]] += v
    return min(groups, key=groups.get)


# ==========================================================
# 4. MY HIDDEN WEAPONS (점수제 상위 3개 노출)
# ==========================================================

def get_special_stars(saju_dict):
    """
    사주팔자 정밀 분석: 14종 무기 중 '전투력(power_score)'이 높은 상위 3개만 리턴
    """
    weapons = []
    
    # 데이터 준비
    branches = [saju_dict['year'][1], saju_dict['month'][1], saju_dict['day'][1]]
    if saju_dict.get('hour'): branches.append(saju_dict['hour'][1])
    
    stems = [saju_dict['year'][0], saju_dict['month'][0], saju_dict['day'][0]]
    if saju_dict.get('hour'): stems.append(saju_dict['hour'][0])
    
    pillars = [saju_dict['year'], saju_dict['month'], saju_dict['day']]
    if saju_dict.get('hour'): pillars.append(saju_dict['hour'])

    day_gan = saju_dict['day_gan'] # 일간 (나)
    day_zhi = saju_dict['day'][1]  # 일지
    day_pillar = saju_dict['day']  # 일주

    # ------------------------------------------------------
    # 1. 도화살 (PEACH BLOSSOM) - B Tier (50~70점)
    # ------------------------------------------------------
    dohwa_list = ['자', '오', '묘', '유']
    count = sum(1 for c in branches if c in dohwa_list)
    if count > 0:
        power = "Lv.MAX" if count >= 3 else f"Lv.{count}"
        score = 50 + (count * 10) # 1개 60점, 2개 70점, 3개 80점
        weapons.append({
            'name': 'PEACH BLOSSOM (도화)',
            'icon': '🌸',
            'desc': '만인의 연인! 숨만 쉬어도 시선이 집중되는 아이돌 오라.',
            'stat': f'ATTRACTION {power}',
            'color': '#ff007f',
            'power_score': score
        })

    # ------------------------------------------------------
    # 2. 역마살 (VOYAGER) - B Tier (50~70점)
    # ------------------------------------------------------
    yeokma_list = ['인', '신', '사', '해']
    count = sum(1 for c in branches if c in yeokma_list)
    if count > 0:
        score = 50 + (count * 10)
        weapons.append({
            'name': 'VOYAGER (역마)',
            'icon': '🐎',
            'desc': '한곳에 멈추면 에러 나는 글로벌 엔진.',
            'stat': 'MOBILITY +100',
            'color': '#00d2d3',
            'power_score': score
        })

    # ------------------------------------------------------
    # 3. 화개살 (MAESTRO) - A Tier (75점)
    # ------------------------------------------------------
    hwagae_list = ['진', '술', '축', '미']
    if any(char in branches for char in hwagae_list):
        weapons.append({
            'name': 'MAESTRO (화개)',
            'icon': '🎨',
            'desc': '고독 속에서 피어나는 천재적 예술성과 철학.',
            'stat': 'ARTISTRY +100',
            'color': '#f1c40f',
            'power_score': 75 
        })

    # ------------------------------------------------------
    # 4. 천을귀인 (NOBLE PATRON) - God Tier (95점)
    # ------------------------------------------------------
    cheon_eul_map = {
        '갑': ['축', '미'], '무': ['축', '미'], '경': ['축', '미'],
        '을': ['자', '신'], '기': ['자', '신'],
        '병': ['해', '유'], '정': ['해', '유'],
        '신': ['인', '오'], '임': ['사', '묘'], '계': ['사', '묘']
    }
    target_zhis = cheon_eul_map.get(day_gan, [])
    if any(z in branches for z in target_zhis):
        weapons.append({
            'name': 'NOBLE PATRON (천을귀인)',
            'icon': '👑',
            'desc': '절벽 끝에서도 밧줄이 내려오는 우주적 VIP 프리패스.',
            'stat': 'LUCK +999',
            'color': '#9b59b6',
            'power_score': 95 # 매우 높음
        })

    # ------------------------------------------------------
    # 5. 백호살 (WHITE TIGER) - S Tier (85점)
    # ------------------------------------------------------
    baekho_pillars = ['갑진', '을미', '병술', '정축', '무술', '임술', '계축']
    if any(p in baekho_pillars for p in pillars):
        weapons.append({
            'name': 'WHITE TIGER (백호)',
            'icon': '🐯',
            'desc': '피를 봐야 직성이 풀리는 압도적 프로페셔널 에너지.',
            'stat': 'POWER +200',
            'color': '#e74c3c',
            'power_score': 85
        })

    # ------------------------------------------------------
    # 6. 현침살 (SHARP NEEDLE) - C Tier (60점)
    # ------------------------------------------------------
    needle_score = 0
    for s in stems:
        if s in ['갑', '신']: needle_score += 1
    for b in branches:
        if b in ['묘', '오', '신']: needle_score += 1
    
    if needle_score >= 2:
        weapons.append({
            'name': 'SHARP NEEDLE (현침)',
            'icon': '💉',
            'desc': '1px의 오차도 허용하지 않는 정밀 타격 스나이퍼.',
            'stat': 'PRECISION +100',
            'color': '#bdc3c7',
            'power_score': 60
        })

    # ------------------------------------------------------
    # 7. 괴강살 (THE BOSS) - God Tier (90점)
    # ------------------------------------------------------
    goegang_pillars = ['경진', '경술', '임진', '임술', '무술']
    if day_pillar in goegang_pillars:
        weapons.append({
            'name': 'THE BOSS (괴강)',
            'icon': '💪',
            'desc': '미친 멘탈과 카리스마. 리더가 아니면 적성이 안 풀림.',
            'stat': 'DOMINANCE +MAX',
            'color': '#2c3e50',
            'power_score': 90
        })

    # ------------------------------------------------------
    # 8. 귀문관살 (DARK MAGE) - S Tier (80점)
    # ------------------------------------------------------
    gwimun_pairs = [
        {'자', '유'}, {'축', '오'}, {'인', '미'}, 
        {'묘', '신'}, {'진', '해'}, {'사', '술'}
    ]
    my_branches_set = set(branches)
    is_gwimun = False
    for pair in gwimun_pairs:
        if pair.issubset(my_branches_set):
            is_gwimun = True
            break
    if is_gwimun:
        weapons.append({
            'name': 'DARK MAGE (귀문)',
            'icon': '👻',
            'desc': '천재와 돌아이 사이. 남들이 못 보는 것을 꿰뚫어 보는 영감.',
            'stat': 'INTUITION +200',
            'color': '#8e44ad',
            'power_score': 80
        })

    # ------------------------------------------------------
    # 9. 홍염살 (RED VELVET) - A Tier (70점)
    # ------------------------------------------------------
    hongyeom_map = {
        '갑': ['오'], '을': ['오'], '병': ['인'], '정': ['미'],
        '무': ['진'], '기': ['진'], '경': ['술'], '신': ['유'],
        '임': ['자', '신'], '계': ['신']
    }
    if day_zhi in hongyeom_map.get(day_gan, []):
        weapons.append({
            'name': 'RED VELVET (홍염)',
            'icon': '🌹',
            'desc': '작정하고 꼬시면 100% 넘어오는 치명적인 저격형 매력.',
            'stat': 'CHARM +150',
            'color': '#ff5e57',
            'power_score': 70
        })

    # ======================================================
    # 🛡️ [FILTER] 상위 3개만 추출 (점수 높은 순 정렬)
    # ======================================================
    # 점수(power_score) 내림차순 정렬
    weapons.sort(key=lambda x: x['power_score'], reverse=True)
    
    # 상위 3개 자르기
    final_weapons = weapons[:3]

    # ======================================================
    # 🛡️ [FAILSAFE] 만약 아무 무기도 없다면? (100% 보장 로직)
    # ======================================================
    if not final_weapons:
        my_element = OHENG_MAP.get(day_gan, '토')
        
        defaults = {
            '목': {'name': 'WILD GROWTH (야생)', 'icon': '🌿', 'desc': '밟혀도 다시 일어나는 좀비 같은 회복력.', 'stat': 'RESILIENCE +100', 'color': '#2ecc71', 'power_score': 10},
            '화': {'name': 'BLAZE HEART (심장)', 'icon': '🔥', 'desc': '꺼지지 않는 열정의 무한 동력 엔진.', 'stat': 'ENERGY +100', 'color': '#e74c3c', 'power_score': 10},
            '토': {'name': 'TITAN CORE (태산)', 'icon': '⛰️', 'desc': '어떤 시련에도 흔들리지 않는 절대 멘탈.', 'stat': 'DEFENSE +100', 'color': '#f39c12', 'power_score': 10},
            '금': {'name': 'STEEL EDGE (강철)', 'icon': '⚔️', 'desc': '한번 물면 놓지 않는 결단력과 맺고 끊음.', 'stat': 'WILLPOWER +100', 'color': '#95a5a6', 'power_score': 10},
            '수': {'name': 'OCEAN MIND (심해)', 'icon': '💧', 'desc': '어디든 스며들고 무엇이든 담아내는 유연함.', 'stat': 'WISDOM +100', 'color': '#3498db', 'power_score': 10},
        }
        
        fallback_weapon = defaults.get(my_element, defaults['토'])
        final_weapons.append(fallback_weapon)
        
    return final_weapons


# ==========================================================
# 5. MAIN INTERFACE
# ==========================================================

def analyze_saju(year, month, day, hour=None, minute=0, gender='male', calendar_type='solar'):
    try:
        if calendar_type in ['lunar', 'lunar_leap'] and KoreanLunarCalendar:
            calendar = KoreanLunarCalendar()
            is_leap = (calendar_type == 'lunar_leap')
            try:
                calendar.setLunarDate(year, month, day, is_leap)
                year = calendar.solarYear
                month = calendar.solarMonth
                day = calendar.solarDay
            except Exception as e:
                print(f"Lunar Convert Error: {e}")

        # [수정] 자정(00시) 출생일 때 False 처리 방지를 위해 is not None 사용
        saju_year = get_corrected_year(year, month, day, hour if hour is not None else 12, minute)
        year_pillar = get_gan_zhi_year(saju_year)
        month_pillar = get_gan_zhi_month(saju_year, month, day)
        day_pillar, day_gan, day_zhi = get_gan_zhi_day(year, month, day)
        
        hour_pillar = None
        if hour is not None:
            hour_pillar = get_gan_zhi_hour(day_gan, hour, minute)
            
        saju_dict = {
            'year': year_pillar,
            'month': month_pillar,
            'day': day_pillar,
            'hour': hour_pillar if hour_pillar else '',
            'day_gan': day_gan
        }
        
        scores_5, scores_10 = calculate_scores(day_gan, saju_dict)
        counts = calculate_element_counts(saju_dict)
        
        sorted_scores = sorted(scores_10.items(), key=lambda x: x[1], reverse=True)
        main_god = sorted_scores[0][0]
        sub_god = sorted_scores[1][0] if len(sorted_scores) > 1 else main_god
        hidden_god = sorted_scores[2][0] if len(sorted_scores) > 2 else sub_god
        
        weakest = get_weakest_group(scores_10)
        strongest_element = max(counts, key=counts.get) if counts else '토'
        weakest_element = min(counts, key=counts.get) if counts else '수'
        strongest_5deity = max(scores_5, key=scores_5.get)
        
        # [KEY] HIDDEN WEAPONS 계산 호출 (Top 3 필터링 적용됨)
        my_weapons = get_special_stars(saju_dict)

        return {
            'saju': saju_dict,
            'scores': scores_5,
            'scores_10': scores_10,
            'counts': counts,
            'strongest': strongest_element,
            'weakest_element': weakest_element,
            'strongest_10': main_god,
            'sub_10': sub_god,
            'hidden_10': hidden_god,
            'weakest': weakest,
            'weakest_5': weakest,
            'strongest_5': strongest_element,
            'weapons': my_weapons 
        }

    except Exception as e:
        print(f"Logic Error: {e}")
        return None