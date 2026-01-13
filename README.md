# 🤖 PERSO Auto Tester

PERSO.AI 더빙 서비스 자동화 QA 테스트 시스템

FastAPI + Playwright 기반의 E2E 테스트 자동화 도구

## ✨ 주요 기능

### 🔐 로그인 테스트 (`test_login`)
- 이메일/비밀번호 로그인 자동화
- 팝업 자동 닫기
- 로그인 성공 여부 확인

### 📤 업로드 테스트 (`test_upload`)
- 영상 파일 자동 업로드
- 번역 설정 모달 감지
- HubSpot 오버레이 제거

### 🌏 번역 테스트 (`test_translate`)
- 원본 언어 선택 (Korean)
- 번역 언어 선택 (English)
- 번역하기 버튼 클릭
- 서비스 이용 동의
- 가이드 팝업 닫기 (2단계)
- 영상 처리 확인

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pdm install
pdm run playwright install chromium
pdm run playwright install-deps
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일 수정:
```env
PERSO_EMAIL=your-email@example.com
PERSO_PASSWORD=your-password
VIDEO_FILE_PATH=./test_videos/sample.mp4
PERSO_URL=https://perso.ai/ko/workspace/vt
HEADLESS=false
```

### 3. 테스트 실행
```bash
# 로그인 테스트
pdm run test_login

# 업로드 테스트
pdm run test_upload

# 번역 테스트 (전체 플로우)
pdm run test_translate

# 웹 서버 실행
pdm run dev
# http://localhost:8000
```

## 🏗️ 프로젝트 구조
```
perso-auto-tester/
├── api/
│   ├── main.py              # FastAPI 메인
│   └── routers/
│       └── test.py          # WebSocket 테스트 라우터
├── tasks/
│   ├── test_login.py        # 로그인 테스트
│   ├── test_upload.py       # 업로드 테스트
│   └── test_translate.py    # 번역 테스트 (전체 플로우)
├── utils/
│   ├── config.py            # 환경변수 로드
│   └── popup_handler.py     # 팝업 처리 유틸
├── templates/
│   └── index.html           # 웹 UI
├── test_videos/
│   └── sample.mp4           # 테스트용 영상
└── pyproject.toml
```

## 🛠️ 기술 스택

- **Python 3.12**
- **FastAPI** - 웹 서버
- **Playwright** - 브라우저 자동화
- **PDM** - 패키지 관리
- **WebSocket** - 실시간 로그 전송

## 📸 스크린샷

테스트 완료 시 자동으로 스크린샷 저장:
- `/tmp/screenshots/login_success.png`
- `/tmp/screenshots/upload_modal.png`
- `/tmp/screenshots/translate_success.png`

## 🔧 주요 해결 과제

### HubSpot 오버레이 문제
- **문제**: HubSpot 마케팅 오버레이가 클릭 방해
- **해결**: STEP 2, 4에서 오버레이 제거

### 드롭다운 선택 불가
- **문제**: 일반 클릭으로 언어 선택 실패
- **해결**: 좌표 기반 클릭 (coordinate-based click)

### 모달 자동 닫힘
- **문제**: Escape 키로 번역 설정 모달까지 닫힘
- **해결**: 모달 배경 클릭으로 드롭다운만 닫기

### 가이드 팝업 2단계
- **문제**: "Next" → "Done" 2단계 팝업
- **해결**: 순차적 팝업 닫기 구현

## 🌐 배포

### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: perso-auto-tester
services:
  - name: web
    github:
      repo: griotold-peach/perso-auto-tester
      branch: main
    build_command: pdm install && pdm run playwright install chromium --with-deps
    run_command: pdm run dev
    envs:
      - key: PERSO_EMAIL
      - key: PERSO_PASSWORD
      - key: VIDEO_FILE_PATH
        value: ./test_videos/sample.mp4
      - key: HEADLESS
        value: "true"
```

배포 URL: https://perso-auto-tester-39ind.ondigitalocean.app

## 📝 테스트 시나리오

### 번역 테스트 전체 플로우
1. ✅ 로그인
2. ✅ 팝업/모달 닫기 (HubSpot 오버레이 포함)
3. ✅ 파일 업로드
4. ✅ 번역 설정 모달 확인
5. ✅ 원본 언어: Korean 선택
6. ✅ 번역 언어: English 선택
7. ✅ 번역하기 버튼 클릭
8. ✅ 서비스 이용 동의
9. ✅ 가이드 팝업 닫기 (2단계)
10. ✅ 영상 처리 확인

## 🤝 기여

이 프로젝트는 EST soft QA 팀의 자동화 테스트를 위해 개발되었습니다.

## 📄 라이선스

MIT License