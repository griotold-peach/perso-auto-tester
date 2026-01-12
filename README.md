cat > README.md << 'EOF'
# PERSO Auto Tester

🤖 PERSO AI 더빙 서비스 자동화 QA 테스트 시스템

[![Deployment](https://img.shields.io/badge/deployed-DigitalOcean-0080FF)](https://perso-auto-tester-39ind.ondigitalocean.app)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.57-red)](https://playwright.dev/)

---

## 🎯 기능

- 🔐 **로그인 자동화**: PERSO.AI 로그인 프로세스 자동 검증
- 📤 **영상 업로드**: 영상 파일 업로드 자동화 (개발 중)
- 🌏 **번역 프로세스**: 번역 설정 및 실행 검증 (개발 중)
- 📡 **실시간 로그**: WebSocket 기반 실시간 로그 스트리밍
- 📸 **자동 스크린샷**: 테스트 성공/실패 시 자동 캡처

---

## 🚀 빠른 시작

### 웹 UI (QA/상사용)

**접속**: https://perso-auto-tester-39ind.ondigitalocean.app

1. 링크 접속
2. "🔐 로그인 테스트" 버튼 클릭
3. 실시간 로그 확인
4. 스크린샷으로 결과 확인

**⚠️ 주의**: 웹 UI는 headless 모드로 실행되어 브라우저 창이 보이지 않습니다.

**💡 크롬 브라우저를 직접 보고 싶으신가요?**
→ [실시간 브라우저 확인 가이드](docs/REALTIME_BROWSER_VIEWING.md)

---

### 로컬 개발 (개발자용)
```bash
# 1. 클론
git clone https://github.com/griotold-peach/perso-auto-tester.git
cd perso-auto-tester

# 2. 설치
pdm install
pdm run playwright install chromium

# 3. 환경변수 설정
cp .env.example .env
# .env 파일 수정 (로그인 정보 입력)

# 4. 테스트 실행 (크롬 창 뜸!)
pdm run test_login       # 로그인 테스트
pdm run test_upload      # 업로드 테스트 (개발 중)

# 5. 웹 서버 실행
pdm run dev              # http://localhost:8000
```

---

## 📖 문서

- **[실시간 브라우저 확인](docs/REALTIME_BROWSER_VIEWING.md)**: 크롬 브라우저로 실시간 확인하는 방법 (상사/QA팀용)

---

## 🏗️ 프로젝트 구조
```
perso-auto-tester/
├── api/                     # FastAPI 백엔드
│   ├── main.py             # 메인 앱
│   └── routers/
│       ├── pages.py        # HTML 페이지
│       └── test.py         # WebSocket API
├── tasks/                   # 테스트 스크립트
│   ├── test_login.py       # 로그인 테스트
│   └── test_upload.py      # 업로드 테스트 (개발 중)
├── utils/                   # 유틸리티
│   ├── config.py           # 환경 설정
│   ├── login.py            # 로그인 함수
│   └── popup_handler.py    # 팝업 처리
├── test_videos/            # 테스트 영상
│   └── sample.mp4
├── docs/                   # 📚 문서
│   └── REALTIME_BROWSER_VIEWING.md
└── Dockerfile              # 도커 이미지
```

---

## 🔧 주요 명령어
```bash
# 테스트 실행 (크롬 창 보임)
pdm run test_login          # 로그인 테스트
pdm run test_upload         # 업로드 + 번역 테스트

# 웹 서버
pdm run dev                 # 개발 서버 (hot reload)
pdm run start               # 프로덕션 서버

# 의존성 관리
pdm add package-name        # 패키지 추가
pdm install                 # 설치
pdm update                  # 업데이트

# Playwright
pdm run playwright install chromium
pdm run playwright install-deps
```

---

## 🌊 배포

`main` 브랜치에 push하면 DigitalOcean에서 자동 배포:
```bash
git push origin main
```

---
