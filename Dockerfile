# 1. 베이스 이미지 (Python 3.12 slim)
FROM python:3.12-slim

# 2. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 3. 워킹 디렉토리
WORKDIR /app

# 4. 시스템 의존성 (Playwright + Chromium 필요)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 5. PDM 설치
RUN pip install --no-cache-dir pdm

# 6. 의존성 파일만 먼저 복사 (레이어 캐싱)
COPY pyproject.toml pdm.lock* /app/

# 7. 파이썬 패키지 설치 (프로덕션 모드)
RUN pdm install --prod --no-lock --no-editable

# 8. Playwright Chromium 설치
RUN pdm run playwright install chromium
RUN pdm run playwright install-deps chromium

# 9. 앱 코드 및 테스트 영상 복사
COPY . /app

# 10. 포트 (App Platform 기본 8080)
EXPOSE 8080

# 11. Uvicorn으로 FastAPI 실행
CMD ["pdm", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
