import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import SCREENSHOT_DIR
from api.routers import test, pages

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("perso-auto-tester")

# FastAPI 앱 생성
app = FastAPI(
    title="PERSO Auto Tester",
    description="🤖 PERSO AI 자동화 테스트",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 스크린샷 디렉토리를 정적 파일로 서빙
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOT_DIR)), name="screenshots")

# 헬스 체크
@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("Health check called")
    return {
        "status": "ok",
        "service": "PERSO Auto Tester",
        "version": "1.0.0"
    }

# 라우터 등록
app.include_router(pages.router, tags=["pages"])
app.include_router(test.router, prefix="/test", tags=["test"])

logger.info("PERSO Auto Tester API initialized")
