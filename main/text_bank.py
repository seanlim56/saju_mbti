import random
import re
import zlib

# [NEW] 확장 데이터 모듈 import
try:
    from .seeds_b_mbti import MBTI_LOVE_SEEDS_V1, MBTI_WORK_SEEDS_V1, MBTI_SPACE_SEEDS_V1
    from .seeds_c_elements import ELEMENT_SEEDS_V1, ELEMENT_IMBALANCE_SEEDS_V1
except ImportError:
    MBTI_LOVE_SEEDS_V1 = {}
    MBTI_WORK_SEEDS_V1 = {}
    MBTI_SPACE_SEEDS_V1 = {}
    ELEMENT_SEEDS_V1 = {}
    ELEMENT_IMBALANCE_SEEDS_V1 = {}


# =========================================================
# 0. CONFIG (설정값)
# =========================================================
SHOW_GOD_TERM = False  # True로 바꾸면 '비견', '겁재' 같은 용어가 같이 표시됨


# =========================================================
# 1. HELPER FUNCTIONS
# =========================================================

def stablepickn(options, keystr, n=2):
    if not options: return []
    options = [o for o in options if o and str(o).strip()]
    if not options: return []
    m = len(options)
    if n >= m:
        rnd = random.Random(zlib.crc32(keystr.encode("utf-8")))
        shuffled = options[:]
        rnd.shuffle(shuffled)
        return shuffled

    h = zlib.crc32(keystr.encode("utf-8"))
    indices = list(range(m))
    selected = []
    for i in range(n):
        idx = (h + i * 12345) % len(indices)
        selected.append(indices.pop(idx))
    return [options[i] for i in selected]


def _unique_preserve(seq):
    seen = set()
    out = []
    for x in seq or []:
        if x in seen: continue
        seen.add(x)
        out.append(x)
    return out


def clean_text(text):
    text = (text or "").replace("**", "")
    # [수정] 🦴 이모지와 '팩폭 분석:' 등의 텍스트를 완벽하게 제거하여 중복 출력 방지
    text = re.sub(r"^(🦴\s*)?(팩폭\s*분석:|팩폭:|팩트\s*체크:|Check:|뼈:|순살:)\s*", "", text).strip()
    return text


def _is_check_line(raw: str) -> bool:
    s = (raw or "").strip()
    return bool(re.search(r"(팩폭|팩트\s*체크|\bCheck\b|뼈|순살)", s, flags=re.IGNORECASE))


def joinps(paragraphs, add_check_box=True):
    if not paragraphs: return ""

    normal_lines, check_lines, highlight_lines = [], [], []
    for p in paragraphs:
        p = str(p).strip()
        if not p: continue
        # ⚖️ 이모지가 있는 모순 해결(입체적 성향) 문장은 따로 분리하여 강조
        if p.startswith("⚖️"):
            highlight_lines.append(clean_text(p))
        elif _is_check_line(p):
            check_lines.append(clean_text(p))
        else:
            normal_lines.append(clean_text(p))

    html_parts = []
    
    # 1. 모순 해결(입체적 성향) 문장을 제일 먼저 노출
    if highlight_lines:
        for hl in highlight_lines:
            html_parts.append(f'<div class="analysis-text" style="color:var(--accent-neon); font-weight:bold; margin-bottom:12px; background:rgba(0, 210, 211, 0.05); padding:10px; border-radius:8px;">{hl}</div>')

    # 2. 일반 특징 리스트화
    current_list = []
    for p in normal_lines:
        if not p: continue
        if "✅" in p or "오늘의 액션" in p or p.startswith("👉") or p.startswith("-") or p.startswith("*"):
            clean = p.replace("✅", "").replace("오늘의 액션:", "").replace("👉", "").lstrip("-* ").strip()
            current_list.append(clean)
            continue

        if current_list:
            items_html = "".join([f'<li class="analysis-item">{x}</li>' for x in current_list])
            html_parts.append(f'<ul class="analysis-list">{items_html}</ul>')
            current_list = []

        html_parts.append(f'<div class="analysis-text" style="margin-bottom:8px;">{p}</div>')

    if current_list:
        items_html = "".join([f'<li class="analysis-item">{x}</li>' for x in current_list])
        html_parts.append(f'<ul class="analysis-list">{items_html}</ul>')

    # 3. 팩폭 박스를 맨 마지막에 노출 (이모지 중복 방지)
    if add_check_box and check_lines:
        check_lines = _unique_preserve([x for x in check_lines if x])
        check_content = "<br>".join([f"🦴 {line}" for line in check_lines[:3]])
        check_box = f"""
        <div style="background:rgba(255, 80, 80, 0.15); border:1px solid rgba(255, 80, 80, 0.4); padding:12px; border-radius:8px; margin-top:15px; font-size:0.92em;">
            <strong style="color:#ff6b6b;">⚡ 심층 팩트 체크</strong><br>
            <div style="color:#eee; margin-top:6px; line-height:1.5;">{check_content}</div>
        </div>
        """
        html_parts.append(check_box)

    return "".join(html_parts)


def normalizembti(mbti): return mbti.strip().upper() if mbti else "XXXX"

def axesdictmbti(m):
    m = normalizembti(m)
    if len(m) != 4: return {}
    return {"EI": m[0], "SN": m[1], "TF": m[2], "JP": m[3]}

def normalizeelement(elem):
    return {"목": "목", "화": "화", "토": "토", "금": "금", "수": "수"}.get(str(elem).strip(), "토")

def god_group(god10: str) -> str:
    if god10 in ("비견", "겁재"): return "비겁"
    if god10 in ("식신", "상관"): return "식상"
    if god10 in ("편재", "정재"): return "재성"
    if god10 in ("편관", "정관"): return "관성"
    if god10 in ("편인", "정인"): return "인성"
    return "비겁"

def make_axis_tags(mbti_dict):
    tags = []
    if mbti_dict.get("EI"): tags.append(f"{mbti_dict['EI']}타입")
    if mbti_dict.get("SN"): tags.append(f"{mbti_dict['SN']}타입")
    if mbti_dict.get("TF"): tags.append(f"{mbti_dict['TF']}타입")
    if mbti_dict.get("JP"): tags.append(f"{mbti_dict['JP']}타입")
    return tags

def _elem_state(elem, element_counts):
    c = int((element_counts or {}).get(elem, 0) or 0)
    if c <= 0: return "lack"
    if c >= 4: return "excess"
    return None


# =========================================================
# 2. DATA BANKS & PROFILES
# =========================================================

_SECTIONKEY = {
    "personality": "identity",
    "money": "money",
    "love": "love",
    "job": "job",
    "housing": "housing",
}

SECTIONBANKS = {
    "personality": [], "money": [], "love": [], "job": [], "housing": [],
    "hidden_engine": [], "management_gap": [], "safety_line": [], "today": [],
}

# [FIX] Django dev 서버 auto-reload 시 중복 실행 방지
_bootstrapped = False

GOD_NICKNAME = {
    "비견": "자기확신형(마이웨이)", "겁재": "승부본능형(경쟁러)",
    "식신": "장인형(몰입러)", "상관": "반골형(팩폭러)",
    "편재": "확장형(판키우는 타입)", "정재": "관리형(실속러)",
    "편관": "돌파형(해결사)", "정관": "원칙형(FM 리더)",
    "편인": "통찰형(의심 많은 천재)", "정인": "수용형(케어받는 타입)",
}

def god_alias(god10: str) -> str: return GOD_NICKNAME.get(god10, str(god10))
def god_label(god10: str) -> str: return f"[{god_alias(god10)}]"

MBTI_GOD_CHEMISTRY = {
    "E": {"비겁": "브레이크 고장난 덤프트럭", "식상": "마이크 잡으면 안 놓는 스타일", "재성": "사람이 곧 돈이고 기회", "관성": "동네 반장부터 대통령까지", "인성": "술자리에서 인생 상담하는 형"},
    "I": {"비겁": "건드리면 무서운 은둔 고수", "식상": "방구석 천재 아티스트", "재성": "조용히 건물주 되는 타입", "관성": "걸어 다니는 법전", "인성": "속을 알 수 없는 현자"},
}

MBTI_PROFILE = {
    "ENTP": {"tell": ["'근데 그게 말이 돼?'가 입버릇"], "trigger": ["논리 없이 '그냥 해'라고 강요받을 때"], "money_leak": ["새로운 취미 장비 풀세트 구매"], "love_habit": ["논쟁을 사랑의 대화로 착각함"], "work_win": ["맨땅에 헤딩하는 신사업"], "work_risk": ["뒷심 부족으로 마무리는 남에게 떠넘김"]},
    "INTP": {"tell": ["영혼 없는 리액션('아 진짜요?')"], "trigger": ["멍 때리는데 말 걸 때"], "money_leak": ["하드웨어/전자기기 업그레이드"], "love_habit": ["상대 감정을 데이터 분석하듯 해석함"], "work_win": ["시스템 허점 찾기"], "work_risk": ["실행 안 하고 시뮬레이션만 돌리다 끝남"]},
    "ENTJ": {"tell": ["답답하면 본인이 직접 해야 직성 풀림"], "trigger": ["일 못하는 사람이 핑계 댈 때"], "money_leak": ["자기계발/강의 결제"], "love_habit": ["연애도 프로젝트처럼 효율적으로 함"], "work_win": ["리더십/팀 빌딩"], "work_risk": ["독재하다 팀원 다 떠남"]},
    "INTJ": {"tell": ["표정이 기본적으로 화난 것 같음"], "trigger": ["예고 없는 약속 변경"], "money_leak": ["전문 서적/지식 콘텐츠"], "love_habit": ["조건/가치관 안 맞으면 칼같이 정리"], "work_win": ["큰 그림 설계/전략"], "work_risk": ["타인의 감정을 변수로 계산 안 함"]},
    "ENFP": {"tell": ["텐션이 롤러코스터"], "trigger": ["디테일한 엑셀 작업"], "money_leak": ["예쁜 쓰레기 수집"], "love_habit": ["금사빠 금사식"], "work_win": ["분위기 메이커/동기부여"], "work_risk": ["벌려놓은 일 수습 불가"]},
    "INFP": {"tell": ["망상 하느라 말 못 들음"], "trigger": ["가치관 공격당할 때"], "money_leak": ["감성 소품/다꾸"], "love_habit": ["운명적 사랑을 꿈꿈"], "work_win": ["예술/글쓰기/창작"], "work_risk": ["멘탈 터지면 잠수탐"]},
    "ENFJ": {"tell": ["오지랖 태평양급"], "trigger": ["배신/뒷담화"], "money_leak": ["모임/회식비 쏘기"], "love_habit": ["헌신하다 헌신짝 됨"], "work_win": ["교육/코칭/멘토링"], "work_risk": ["모두에게 좋은 사람 되려다 과로사"]},
    "INFJ": {"tell": ["겉으론 웃는데 속으론 손절 각 잼"], "trigger": ["예의 없는 행동"], "money_leak": ["인테리어/향기/분위기"], "love_habit": ["도어슬램(마음의 문 닫음) 전문"], "work_win": ["심리 상담/인사"], "work_risk": ["완벽주의 때문에 시작을 못 함"]},
    "ESTP": {"tell": ["일단 저지르고 수습은 나중에"], "trigger": ["빙빙 돌려 말하기"], "money_leak": ["유흥/파티/술값"], "love_habit": ["오는 사람 안 막고 가는 사람 안 잡음"], "work_win": ["영업/현장직"], "work_risk": ["리스크 관리 안 하고 올인"]},
    "ISTP": {"tell": ["'굳이?'가 인생 모토"], "trigger": ["감정 쓰레기통 취급"], "money_leak": ["취미 장비(기계식 키보드, 자전거)"], "love_habit": ["구속하면 도망감"], "work_win": ["기술적 문제 해결"], "work_risk": ["최소한의 일만 하려 함"]},
    "ESTJ": {"tell": ["팩폭 머신"], "trigger": ["무능한데 게으른 사람"], "money_leak": ["브랜드/명품(과시용)"], "love_habit": ["데이트 통장 엑셀 정리"], "work_win": ["조직 관리/운영"], "work_risk": ["융통성 없어서 적으로 만듦"]},
    "ISTJ": {"tell": ["걸어 다니는 로봇"], "trigger": ["급작스러운 번개"], "money_leak": ["안정적인 적금/보험"], "love_habit": ["신뢰가 최우선"], "work_win": ["회계/재무/관리"], "work_risk": ["새로운 시도 자체를 거부"]},
    "ESFP": {"tell": ["관종(관심 못 받으면 시무룩)"], "trigger": ["진지한 분위기"], "money_leak": ["외모 치장/패션"], "love_habit": ["열정적이고 이벤트 좋아함"], "work_win": ["서비스/엔터테인먼트"], "work_risk": ["싫증을 빨리 냄"]},
    "ISFP": {"tell": ["귀차니즘 만렙"], "trigger": ["결단 강요"], "money_leak": ["집 꾸미기(침구류)"], "love_habit": ["짝사랑 전문"], "work_win": ["예술/디자인"], "work_risk": ["기한(Deadline) 못 지킴"]},
    "ESFJ": {"tell": ["리액션 기계"], "trigger": ["불화/왕따"], "money_leak": ["선물/밥값"], "love_habit": ["애정 결핍"], "work_win": ["협력/지원 업무"], "work_risk": ["비판을 개인적 비난으로 받아들임"]},
    "ISFJ": {"tell": ["착한 아이 콤플렉스"], "trigger": ["무례함"], "money_leak": ["가족/지인을 위한 지출"], "love_habit": ["헌신적이고 세심함"], "work_win": ["비서/보조/지원"], "work_risk": ["거절 못해서 업무 독박 씀"]},
}

GOD_PROFILE = {
    "비견": {"drive": ["'내가 짱이다' 증명 욕구"], "shadow": ["타협하면 자존심 스크래치"], "tell": ["남 밑에선 절대 못 일함"]},
    "겁재": {"drive": ["'쟤는 이긴다' 경쟁심"], "shadow": ["질투심 폭발"], "tell": ["적을 만들어서 성장함"]},
    "식신": {"drive": ["'재밌으니까 하지'"], "shadow": ["싫으면 죽어도 안 함"], "tell": ["먹는 거에 진심"]},
    "상관": {"drive": ["'이거 아니지 않아요?' 반론"], "shadow": ["말실수로 적 만듦"], "tell": ["팩폭 장인"]},
    "편재": {"drive": ["'전국 제패' 확장 욕구"], "shadow": ["마무리가 안 됨"], "tell": ["돈 냄새 기가 막히게 맡음"]},
    "정재": {"drive": ["'티끌 모아 태산'"], "shadow": ["짠돌이/짠순이"], "tell": ["가계부 1원까지 맞춤"]},
    "편관": {"drive": ["'나를 따르라' 카리스마"], "shadow": ["강박관념/스트레스"], "tell": ["폼생폼사"]},
    "정관": {"drive": ["'법대로 해'"], "shadow": ["융통성 제로"], "tell": ["약속 시간 1분도 안 늦음"]},
    "편인": {"drive": ["'저건 무슨 의미일까?' 의심"], "shadow": ["망상과 게으름"], "tell": ["눈치 100단"]},
    "정인": {"drive": ["'해줘'"], "shadow": ["마마보이/마마걸"], "tell": ["문서운 좋음"]},
}

WEAK5_HINT = {
    "비겁": ["주관이 없어서 팔랑귀 됨. '내 기준'부터 세워야 안 털림."],
    "식상": ["생각만 하다 똥 됨. 일단 저질러야 뭐라도 나옴."],
    "재성": ["현실 감각 제로. 숫자/돈 공부 안 하면 호구 잡힘."],
    "관성": ["절제력 부족. 브레이크 없는 페라리는 사고 남."],
    "인성": ["깊이가 없음. 겉핥기 그만하고 책 좀 읽어야 함."],
}

def _add(sec, ctype, cval, lines):
    for line in lines:
        SECTIONBANKS[sec].append({"type": ctype, "val": cval, "text": line})

def _build_combo_lines(mbti, god10, seed):
    mp = MBTI_PROFILE.get(mbti, {})
    gp = GOD_PROFILE.get(god10, {})

    tell = stablepickn(mp.get("tell", ["특징 없음"]), f"{seed}:tell", 1)[0]
    trig = stablepickn(mp.get("trigger", ["짜증남"]), f"{seed}:trig", 1)[0]
    leak = stablepickn(mp.get("money_leak", ["돈 낭비"]), f"{seed}:leak", 1)[0]
    love = stablepickn(mp.get("love_habit", ["연애 습관"]), f"{seed}:love", 1)[0]
    win = stablepickn(mp.get("work_win", ["성과"]), f"{seed}:win", 1)[0]
    risk = stablepickn(mp.get("work_risk", ["위기"]), f"{seed}:risk", 1)[0]

    drive = stablepickn(gp.get("drive", ["욕구"]), f"{seed}:drive", 1)[0]
    shadow = stablepickn(gp.get("shadow", ["단점"]), f"{seed}:shadow", 1)[0]

    return {
        "personality": [
            # [수정] 괴리감이 아니라 자연스러운 인과관계로 연결되도록 변경
            f"🦴 팩폭 분석: 평소에 남들에게 자주 보여주는 '{tell}' 모습의 진짜 원동력은 사실 깊은 곳에 자리 잡은 {god_label(god10)}의 '{drive}' 때문입니다.",
            f"💡 솔루션: {god_label(god10)}의 '{shadow}' 성향을 스스로 인정하세요. 억누르려다 상황만 꼬입니다. 차라리 겉으로 드러내고 본인의 색깔로 쓰세요.",
        ],
        "money": [
            # [수정] 조사를 매끄럽게 정리
            f"💸 텅장 주의보: {mbti}의 '{leak}' 소비 패턴에 {god_label(god10)}의 '{shadow}' 기질이 합쳐지면 통장이 버티질 못합니다. 확실한 브레이크가 필요합니다.",
        ],
        "love": [
            f"💔 연애 경고: {mbti} 특유의 '{love}' 성향에 {god_label(god10)}의 '{shadow}' 기질이 나오기 시작하면 상대방이 크게 지칠 수 있습니다. 텐션 조절이 필수입니다.",
        ],
        "job": [
            f"💼 일잘러 vs 빌런: '{win}' 업무 영역에선 날아다니지만, 간혹 터지는 '{risk}' 문제로 다 된 밥에 재를 빠뜨릴 수 있습니다.",
        ],
        "hidden_engine": [
            f"🎭 숨겨진 본성: 쿨한 척하지만 마음 깊은 곳에서는 {god_label(god10)}의 '{drive}'에 강력하게 이끌립니다. 이 본능을 충족시켜야 마음이 편해집니다.",
            f"💣 지뢰밭: 평소엔 이성적이다가도 '{trig}' 상황이 오면 참지 못하고 폭주기관차가 됩니다.",
        ],
        "management_gap": [
            f"🛠 관리 필요: 머리로는 '{win}' 쪽을 좇으면서, 막상 몸과 돈은 무의식적으로 '{leak}'에 쏟고 있지 않나요?",
        ],
        "safety_line": [
            f"🚧 안전선: 텐션 높을 때 충동적으로 약속을 잡지 마세요. {mbti} 특성상 나중에 수습 못 할 스케줄을 남발할 확률이 아주 높습니다.",
        ]
    }


def bootstrap_full_data():
    global _bootstrapped
    if _bootstrapped:
        return
    _bootstrapped = True

    _add("today", "global", None, [
        "책상 위 쓰레기 3개 버리기", "카톡 읽지 않은 메시지 정리", "물 500ml 원샷",
        "자기 전 폰 멀리 두기", "오늘 쓴 돈 가계부에 적기", "영양제 챙겨 먹기",
        "엘리베이터 대신 계단 쓰기", "하늘 한 번 쳐다보기", "감사한 일 1개 찾기"
    ])

    for w5, lines in WEAK5_HINT.items():
        _add("hidden_engine", "weak5", w5, lines)

    gods10 = list(GOD_PROFILE.keys())
    for mbti in MBTI_PROFILE.keys():
        for god10 in gods10:
            gen_seed = f"GEN:{mbti}:{god10}"
            combo_lines = _build_combo_lines(mbti, god10, gen_seed)
            for sec, lines in combo_lines.items():
                _add(sec, "combo", (mbti, god10), lines)
                _add(sec, "combo", (mbti, god_group(god10)), lines[:1])

    if MBTI_LOVE_SEEDS_V1:
        for mbti, lines in MBTI_LOVE_SEEDS_V1.items():
            _add("love", "mbti", mbti, lines)
    if MBTI_WORK_SEEDS_V1:
        for mbti, lines in MBTI_WORK_SEEDS_V1.items():
            _add("job", "mbti", mbti, lines)
    if MBTI_SPACE_SEEDS_V1:
        for mbti, lines in MBTI_SPACE_SEEDS_V1.items():
            _add("housing", "mbti", mbti, lines)

    if ELEMENT_SEEDS_V1:
        for elem, pack in ELEMENT_SEEDS_V1.items():
            _add("personality", "element", elem, pack.get("identity", []))
            _add("money", "element", elem, pack.get("money", []))
            _add("love", "element", elem, pack.get("love", []))
            _add("job", "element", elem, pack.get("job", []))
            _add("housing", "element", elem, pack.get("housing", []))

bootstrap_full_data()


# =========================================================
# 3. [UPGRADED] DYNAMIC GENERATION LOGIC (모순 해결기 포함)
# =========================================================

def _generate_deep_analysis(sec, mbti_dict, element, main_god, weakest_five, element_counts):
    """
    MBTI와 사주의 모순을 잡아내어 '입체적 성향'으로 해석해주는 핵심 로직입니다.
    """
    mbti = mbti_dict.get("FULL", "XXXX")
    god_name = god_label(main_god)
    elem_name = normalizeelement(element)
    
    is_E = mbti_dict.get("EI") == "E"
    is_I = mbti_dict.get("EI") == "I"
    is_N = mbti_dict.get("SN") == "N"
    is_S = mbti_dict.get("SN") == "S"
    is_T = mbti_dict.get("TF") == "T"
    is_F = mbti_dict.get("TF") == "F"
    is_J = mbti_dict.get("JP") == "J"
    is_P = mbti_dict.get("JP") == "P"
    
    lines = []

    # ---------------------------------------------------------
    # 🧩 IDENTITY (자아/성격)
    # ---------------------------------------------------------
    if sec == "personality":
        if is_F and element in ["금", "토"]:
            lines.append(f"⚖️ [입체적 성향]: 평소엔 공감 능력이 뛰어난 {mbti}이지만, 본능에는 차가운 {elem_name} 기운이 돌아 '선 넘는 순간 피도 눈물도 없이 손절'하는 반전 냉정함이 공존합니다.")
        elif is_T and element in ["수", "목", "화"]:
            lines.append(f"⚖️ [입체적 성향]: 겉으로는 차가운 논리({mbti_dict['TF']}형)를 굴리는 척하지만, 기저에는 다정다감한 {elem_name} 기운이 배어 있어 결국엔 '알면서도 져주는' 인간미가 튀어나옵니다.")

        if is_P and main_god in ["정관", "정재", "정인"]:
            lines.append(f"⚖️ [입체적 성향]: 겉보기엔 유연하고 룰(Rule)에 얽매이지 않는 영혼({mbti}) 같지만, 속에는 깐깐한 {god_name}이 앉아 있어 묘하게 보수적이고 선비 같은 구석이 있습니다.")
        elif is_J and main_god in ["상관", "편재", "식신"]:
            lines.append(f"⚖️ [입체적 성향]: 철저하게 계획을 세워두고 안심하는 {mbti} 성향과 다르게, 막상 실행할 땐 {god_name}의 즉흥성에 휘말려 다 뒤엎고 새로 직진하는 기분파입니다.")

        if is_E and element == "수":
            lines.append(f"⚖️ [에너지 반전]: 밖에서는 에너지 넘치는 인싸({mbti})지만, 깊은 내면은 수(水) 기운의 고요함을 갈망해 무조건 '혼자 폰 끄고 잠수 타는 충전 시간'이 필요한 타입입니다.")
        elif is_I and element == "화":
            lines.append(f"⚖️ [에너지 반전]: 조용한 내향인({mbti})이지만, 화(火) 기운이 발동하면 나도 모르게 분위기를 주도하는 무대 체질이 되어버리는 '선택적 관종' 기질이 숨어있습니다.")

    # ---------------------------------------------------------
    # 💸 MONEY (재물) 
    # ---------------------------------------------------------
    elif sec == "money":
        if is_N and main_god in ["정재", "정관"]:
            lines.append(f"⚖️ [소비의 반전]: 이상적이고 미래지향적인 {mbti}라 뜬구름 잡는 데 돈을 쓸 것 같지만, {god_name}의 짠돌이 본능 덕분에 현실적인 가계부 계산은 누구보다 철저합니다.")
        elif is_J and main_god in ["편재", "상관"]:
            lines.append(f"⚖️ [소비의 반전]: 예산 엑셀 파일은 기가 막히게 짜놓고, 막상 {god_name}의 꽂히는 무언가가 나타나면 예산 따위 무시하고 통 크게 일시불을 긁어버립니다.")

    # ---------------------------------------------------------
    # 💘 LOVE (연애)
    # ---------------------------------------------------------
    elif sec == "love":
        if is_T and main_god in ["정인", "편인", "식신"]:
            lines.append(f"⚖️ [연애의 온도]: {mbti_dict['TF']}형 특유의 팩트 체크 화법으로 연인을 서운하게 만들 때도 있지만, 속마음은 {god_name}의 맹목적인 애정을 갈구하고 베푸는 외강내유 스타일입니다.")
        elif is_P and main_god in ["정관", "편관"]:
            lines.append(f"⚖️ [연애의 온도]: 연애 초반에는 {mbti}의 자유분방함으로 상대를 끌어당기지만, 관계가 깊어질수록 {god_name}의 '내 사람에 대한 책임감'이 발동해 든든한 방패막이가 되어줍니다.")

    # ---------------------------------------------------------
    # 💼 WORK (직업)
    # ---------------------------------------------------------
    elif sec == "job":
        if is_F and main_god in ["편관", "겁재", "편재"]:
            lines.append(f"⚖️ [일터의 자아]: 동료들과 평화롭게 지내고 싶은 {mbti_dict['TF']}형 마인드와, 일에서만큼은 무조건 1등을 찍어야 직성이 풀리는 {god_name}의 승부욕이 내면에서 매일 충돌합니다.")
        elif is_I and main_god in ["편재", "상관", "비견"]:
            lines.append(f"⚖️ [일터의 자아]: 회식과 네트워킹은 기 빨려하는 {mbti}이지만, 회의나 협상 테이블에 앉으면 {god_name}의 전투력이 발동해 할 말은 기어코 다 하고 내려오는 불도저입니다.")

    # ---------------------------------------------------------
    # 🪐 SPACE (공간)
    # ---------------------------------------------------------
    elif sec == "housing":
        if is_E and element in ["수", "금"]:
            lines.append(f"⚖️ [공간의 의미]: 밖에서 사람들과 에너지를 나누는 {mbti}이기에, 역설적으로 집은 완벽히 단절되고 차가운 {elem_name} 기운으로 정돈되어야만 진짜 회복이 일어납니다.")
        elif is_J and element in ["목", "화"]:
            lines.append(f"⚖️ [공간의 의미]: 각 잡힌 수납을 선호하는 {mbti_dict['JP']}형이지만, 집안 분위기 자체는 생동감 넘치고 따뜻한 {elem_name} 기운(식물/조명)으로 채워야 멘탈이 안정됩니다.")

    return lines


def _pick_section(sec, mbti_dict, element, main_god, weakest_five=None, seed=None, count=10, 
                  weakest_element=None, element_counts=None):
    
    full_mbti = mbti_dict.get("FULL", "XXXX")
    axis_tags = make_axis_tags(mbti_dict)
    g5 = god_group(main_god)
    
    combo_lines, god_lines, mbti_lines, elem_lines, weak_lines, global_lines = [], [], [], [], [], []
    
    for item in SECTIONBANKS.get(sec, []):
        t, v, txt = item.get("type"), item.get("val"), item.get("text")
        if not txt: continue
        if t == "combo":
             try:
                m, g = v
                if m == full_mbti and g in (main_god, g5): combo_lines.append(txt)
             except: pass
        elif t == "god" and v in (main_god, g5): god_lines.append(txt)
        elif t == "mbti" and (v == full_mbti or v in axis_tags): mbti_lines.append(txt)
        elif t == "element" and v == element: elem_lines.append(txt)
        elif t == "weak5" and v == weakest_five: weak_lines.append(txt)
        elif t == "global": global_lines.append(txt)

    deep_lines = _generate_deep_analysis(sec, mbti_dict, element, main_god, weakest_five, element_counts)
    
    def uniq(l): return _unique_preserve(l)
    
    picked_deep = stablepickn(uniq(deep_lines), f"{seed}:deep", 2)
    picked_combo = stablepickn(uniq(combo_lines), f"{seed}:combo", 1)
    
    # Imbalance (C-2)
    picked_imb = []
    sec_key = _SECTIONKEY.get(sec)
    if sec_key and ELEMENT_IMBALANCE_SEEDS_V1:
        strong_state = _elem_state(element, element_counts)
        if strong_state: 
            imb_cands = ELEMENT_IMBALANCE_SEEDS_V1.get(element, {}).get(strong_state, {}).get(sec_key, [])
            picked_imb = stablepickn(uniq(imb_cands), f"{seed}:imb", 1)

    # 나머지 채우기
    rest_cands = uniq(god_lines + elem_lines + mbti_lines + weak_lines + global_lines)
    left = count - (len(picked_deep) + len(picked_combo) + len(picked_imb))
    picked_rest = stablepickn(rest_cands, f"{seed}:rest", left) if left > 0 else []

    # [중요] 배열 순서 강제: 무조건 모순 해결(Deep) 멘트가 제일 먼저 나오도록 설정
    final_list = picked_deep + picked_combo + picked_imb + picked_rest
    return uniq(final_list)


def get_rich_text(mbti, main_god, sub_god=None, weakest_five=None, strongest_element=None, hidden_god=None, seed_key=None,
                  weakest_element=None, element_counts=None):
    mbti = normalizembti(mbti)
    mbti_dict = axesdictmbti(mbti)
    mbti_dict["FULL"] = mbti
    elem = normalizeelement(strongest_element)
    
    if not seed_key:
        seed_key = f"{mbti}:{main_god}:{elem}"

    chem = MBTI_GOD_CHEMISTRY.get(mbti_dict.get("EI", "E"), {}).get(god_group(main_god), "폭발적 시너지 or 대환장 파티")
    intro_html = f"""
    <div style="background:rgba(255,255,255,0.05); padding:16px; border-radius:12px; margin-bottom:20px; border:1px solid rgba(255,255,255,0.1);">
        <strong style="color:#00d2d3; font-size:1.2em; letter-spacing:-0.5px;">🚀 {mbti} x {god_label(main_god)} 심층 분석</strong><br>
        <div style="font-size:0.95em; color:#ddd; margin-top:10px; line-height:1.6;">
            당신의 OS는 <b>{mbti}</b>, 탑재된 핵심 엔진은 <b>{god_label(main_god)}</b>입니다.<br>
            <b>⚡ 케미 요약:</b> {chem}
        </div>
    </div>
    """

    lines_p = _pick_section("personality", mbti_dict, elem, main_god, weakest_five, seed_key, 10, weakest_element, element_counts)
    lines_m = _pick_section("money", mbti_dict, elem, main_god, weakest_five, seed_key, 8, weakest_element, element_counts)
    lines_l = _pick_section("love", mbti_dict, elem, main_god, weakest_five, seed_key, 8, weakest_element, element_counts)
    lines_j = _pick_section("job", mbti_dict, elem, main_god, weakest_five, seed_key, 8, weakest_element, element_counts)
    lines_h = _pick_section("housing", mbti_dict, elem, main_god, weakest_five, seed_key, 6, weakest_element, element_counts)

    lines_hid = _pick_section("hidden_engine", mbti_dict, elem, main_god, weakest_five, seed_key, 3)
    lines_gap = _pick_section("management_gap", mbti_dict, elem, main_god, weakest_five, seed_key, 3)
    lines_safe = _pick_section("safety_line", mbti_dict, elem, main_god, weakest_five, seed_key, 3)
    actions = _pick_section("today", mbti_dict, elem, main_god, weakest_five, seed_key, 5)

    action_html = "".join([f'<li><span class="check-icon">✔</span> {clean_text(x)}</li>' for x in actions])
    action_html = f'<ul class="action-list">{action_html}</ul>'

    identity_html = intro_html + joinps(lines_p, True)
    headline_alias = god_alias(main_god)
    
    return {
        "headline": f"{mbti} x {headline_alias}",
        "identity_core": identity_html,
        "hidden_engine": joinps(lines_hid, True),
        "management_gap": joinps(lines_gap, True),
        "money": joinps(lines_m, True),
        "love": joinps(lines_l, True),
        "job": joinps(lines_j, True),
        "housing": joinps(lines_h, True),
        "safety_line": joinps(lines_safe, True),
        "today_actions": action_html,
        "identitycore": identity_html, "hiddenengine": joinps(lines_hid, True),
        "managementgap": joinps(lines_gap, True), "safetyline": joinps(lines_safe, True),
        "todayactions": action_html,
    }