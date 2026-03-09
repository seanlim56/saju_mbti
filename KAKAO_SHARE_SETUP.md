# 📢 카카오톡 공유 기능 설정 가이드

## 1분 설정다음 단계를 따라하면 카카오톡 공유 기능이 활성화됩니다.

---

## 필수 조건
- 카카오 개발자 계정 (무료)
- JavaScript 키 (카카오 개발자센터에서 발급)

---

## 단계별 가이드

### 1단계: 카카오 개발자 앱 등록

1. https://developers.kakao.com 접속 → 로그인
2. **내 애플리케이션 → 애플리케이션 추가하기** 클릭
3. 앱 이름 입력 (예: "Life Ticket")
4. **플랫폼 설정 → Web 등록** 클릭
   - 사이트 도메인: `https://saju-mbti.onrender.com`
5. **앱 키 → JavaScript 키** 복사해두기

---

### 2단계: 코드에 JavaScript 키 적용

**파일 경로:** `main/templates/main/index.html`

**857번 줄 근처를 찾아 아래 코드를 수정하세요:**

```javascript
// 기존 코드
Kakao.init('YOUR_KAKAO_JS_KEY');  // ⚠️ 여기를 수정!

// → 수정 후
Kakao.init('1234567890abcdef1234567890abcdef');  // 고유한 JavaScript 키로 교체
```

---

### 3단계: DB 마이그레이션 (필수)

Render 또는 로컬 환경에서 실행:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 4단계: 테스트

1. 로그인 → 분석 완료 → **결과 저장** 클릭
2. **📢 카카오톡으로 공유하기** 버튼 클릭
3. 카카오톡에서 공유 카드 확인
4. 친구가 링크 클릭 → 공유 결과 페이지 로드 확인

---

## 공유 URL 구조

```
https://saju-mbti.onrender.com/share/{UUID}/
```

예시:
```
https://saju-mbti.onrender.com/share/a1b2c3d4-1234-5678-90ab-cdef12345678/
```

---

## 트러블슈팅

| 문제 | 해결법 |
|------|--------|
| "실제 JavaScript 키를 입력해주세요" 팝업 | 카카오 개발자센터에서 발급받은 키로 `Kakao.init()` 교체 |
| 공유 버튼이 안 보임 | 결과 저장을 먼저 클릭하세요 (share_token 생성 후 활성화) |
| 공유 링크가 404 에러 | Render에서 `python manage.py migrate` 실행 확인 |

---

## 참고 문서
- [카카오 개발자센터](https://developers.kakao.com)
- [카카오 메시지 API 문서](https://developers.kakao.com/docs/latest/ko/message/js)
