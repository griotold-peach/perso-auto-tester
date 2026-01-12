# 실시간 브라우저 동작 확인 가이드

## 📋 개요

현재 배포된 웹 UI는 **headless 모드**로 실행되어 브라우저 창이 직접 보이지 않습니다.

**QA팀께서 실제 브라우저 동작을 실시간으로 보고 싶으신 경우**, 아래 두 가지 방법이 있습니다.

---

## 🎯 방법 비교

| 방법 | 브라우저 보기 | 설치 시간 | 난이도 | 추천 대상 |
|------|--------------|----------|--------|----------|
| git clone + 로컬 설치 | ✅ | 10분 | 중간 | 개발자, 자주 확인 필요 |
| 데스크톱 앱 | ✅ | 1-2주 | 어려움 | 전체 팀 |

---

## ✅ 방법 1: 로컬 설치 (Git Clone)

### 장점
- ✅ 실제 크롬 브라우저 창이 뜸
- ✅ 단계별로 천천히 동작 확인 가능
- ✅ DevTools로 디버깅 가능
- ✅ 10분이면 설치 완료

### 단점
- ⚠️ Git, Python, PDM 설치 필요
- ⚠️ 명령어 실행 필요 (GUI 없음)

---

### 📦 필수 프로그램

1. **Git**: https://git-scm.com/download
2. **Python 3.12**: https://www.python.org/downloads/
3. **PDM**: 터미널에서 `pip install pdm`

---

### 🔧 설치 단계

#### Windows
```bash
# 1. Git Bash 또는 PowerShell 열기

# 2. 프로젝트 다운로드
git clone https://github.com/griotold-peach/perso-auto-tester.git
cd perso-auto-tester

# 3. 의존성 설치
pdm install

# 4. Playwright Chromium 설치
pdm run playwright install chromium
pdm run playwright install-deps

# 5. 환경변수 설정
# .env 파일 생성 후 로그인 정보 입력
# (자동으로 제공 또는 직접 입력)

# 6. 실행 (크롬 창 뜸!)
pdm run test_login
```

#### Mac
```bash
# 1. 터미널 열기

# 2. 프로젝트 다운로드
git clone https://github.com/griotold-peach/perso-auto-tester.git
cd perso-auto-tester

# 3. 의존성 설치
pdm install

# 4. Playwright Chromium 설치
pdm run playwright install chromium
pdm run playwright install-deps

# 5. 환경변수 설정
cp .env.example .env
# .env 파일 열어서 로그인 정보 입력

# 6. 실행 (크롬 창 뜸!)
pdm run test_login
```

---

### 🎬 실행 화면
```bash
pdm run test_login
```

실행하면:
1. ✅ 크롬 브라우저 창이 자동으로 뜸
2. ✅ PERSO.AI 사이트 접속
3. ✅ 이메일 입력 → 비밀번호 입력 → 로그인
4. ✅ 각 단계가 천천히 진행 (0.5초 딜레이)
5. ✅ 성공/실패 확인 후 브라우저 자동 종료

**스크린샷 저장 위치**: `/tmp/screenshots/login_success.png`

---

### 🆘 문제 해결

#### Git이 없을 때
https://git-scm.com/download 에서 다운로드

#### Python이 없을 때
https://www.python.org/downloads/ 에서 Python 3.12 다운로드

#### PDM 설치 실패
```bash
# Windows
python -m pip install pdm

# Mac
python3 -m pip install pdm
```

#### Playwright 설치 오류
```bash
# 권한 문제 시
pdm run playwright install chromium --with-deps
```

---

## 🚀 방법 2: 데스크톱 앱 개발 (Electron)

### 개요

Windows/Mac용 **데스크톱 애플리케이션**으로 제공

### 장점
- ✅ 아이콘 더블클릭만으로 실행
- ✅ Git, Python 등 설치 불필요
- ✅ 설치 파일(.exe, .dmg) 제공
- ✅ 일반 사용자도 쉽게 사용

### 단점
- ⚠️ 추가 개발 기간 필요: **1-2주**
- ⚠️ 유지보수 추가

---

### 개발 계획

#### 기술 스택
- **Electron**: 크로스 플랫폼 데스크톱 앱
- **React**: UI 프레임워크
- **Playwright**: 브라우저 자동화 (동일)

#### 예상 개발 일정
```
1주차: Electron 앱 기본 구조 + UI
2주차: Playwright 통합 + 빌드/배포
```

#### 최종 산출물
- `perso-auto-tester-setup.exe` (Windows)
- `perso-auto-tester.dmg` (Mac)

---

### 사용자 경험 (개발 후)

1. **설치 파일 다운로드** (한 번만)
2. **설치** (Next → Next → 완료)
3. **바탕화면 아이콘 더블클릭**
4. **"로그인 테스트" 버튼 클릭**
5. **크롬 브라우저 창이 뜨면서 자동 실행**

**→ 가장 사용자 친화적!**

---

### 개발 착수 전 확인사항

- **필요성**: 전체 QA팀이 사용? or 특정 인원만?
- **우선순위**: 다른 기능(업로드/번역) vs 데스크톱 앱
- **예산**: 개발 시간 1-2주 투자 가능?

---

## 🤔 어떤 방법을 선택해야 할까?

### 상황별 추천

**개발자 or 기술에 익숙한 사람:**
→ **방법 1 (로컬 설치)** - 10분이면 끝

**비개발자 or 여러 명이 사용:**
→ **방법 2 (데스크톱 앱)** - 개발 필요

**한두 명만 가끔 확인:**
→ **방법 1 (로컬 설치)** - 한 번만 설치해드리면 됨

**QA팀 전체가 매일 사용:**
→ **방법 2 (데스크톱 앱)** - 투자 가치 있음

---

## 💬 상사/QA팀께 안내 메시지 템플릿
```
현재 배포된 웹 버전은 headless 모드로 실행되어 
브라우저 창이 직접 보이지 않습니다.

실제 브라우저 동작을 확인하시려면 두 가지 방법이 있습니다:

1️⃣ 로컬 설치 (10분 소요)
   - 실제 크롬 창을 보면서 테스트 가능
   - Git, Python 설치 필요
   - 필요 시 직접 설치해드리겠습니다

2️⃣ 데스크톱 앱 개발 (1-2주 소요)
   - 설치 후 아이콘 클릭만으로 실행
   - Windows/Mac 실행 파일 제공
   - 추가 개발 기간 필요

어떤 방법을 원하시나요?
```

---

## 📞 지원

### 직접 설치 지원
10분 정도 시간 내주시면 직접 설치해드릴 수 있습니다.

### 데스크톱 앱 개발 요청
개발 착수 전 요구사항 확인 미팅 필요

### 문의
- GitHub Issues: https://github.com/griotold-peach/perso-auto-tester/issues
- 담당자: griotold
