import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

# 환경변수
VIDEO_FILE_PATH = os.getenv('VIDEO_FILE_PATH', './test_videos/sample.mp4')
if not VIDEO_FILE_PATH.startswith('/'):
    VIDEO_FILE_PATH = str(PROJECT_ROOT / VIDEO_FILE_PATH)

PERSO_EMAIL = os.getenv('PERSO_EMAIL')
PERSO_PASSWORD = os.getenv('PERSO_PASSWORD')
PERSO_URL = os.getenv('PERSO_URL', 'https://perso.ai/ko/workspace/vt')

# Playwright 설정
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'

# 스크린샷 저장 경로
SCREENSHOT_DIR = Path("/tmp/screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

print(f"✅ 설정 로드 완료")
print(f"📧 이메일: {PERSO_EMAIL}")
print(f"🎬 영상 파일: {VIDEO_FILE_PATH}")
print(f"🖥️  Headless: {HEADLESS}")
