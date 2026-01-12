import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import PERSO_EMAIL, PERSO_PASSWORD, HEADLESS, SCREENSHOT_DIR
from utils.login import login

def test_login_sync(log_callback=None):
    """로그인 테스트 (동기 버전)"""
    
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)
    
    log(f"🚀 로그인 테스트 시작")
    log(f"📧 이메일: {PERSO_EMAIL}")
    log(f"🖥️  Headless: {HEADLESS}")
    
    with sync_playwright() as p:
        # 브라우저 설정
        launch_options = {
            'headless': HEADLESS,
        }
        if HEADLESS:
            launch_options['args'] = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        else:
            launch_options['slow_mo'] = 500
        
        browser = p.chromium.launch(**launch_options)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 로그인 페이지 접속
            log("📍 로그인 페이지 접속 중...")
            page.goto('https://perso.ai/ko/login', timeout=30000)
            page.wait_for_load_state('networkidle')
            
            # 이메일 입력
            log("📝 이메일 입력 중...")
            email_input = page.locator('input[type="email"], input[placeholder*="이메일"]')
            email_input.fill(PERSO_EMAIL)
            time.sleep(0.5)
            
            # 계속 버튼 클릭
            log("👆 계속 버튼 클릭...")
            continue_button = page.locator('button:has-text("계속")')
            continue_button.click()
            time.sleep(2)
            
            # 비밀번호 입력
            log("🔐 비밀번호 입력 중...")
            password_input = page.locator('input[type="password"]')
            password_input.fill(PERSO_PASSWORD)
            time.sleep(0.5)
            
            # Enter 키로 로그인
            log("🚪 Enter 키로 로그인 제출...")
            password_input.press('Enter')
            
            # 로그인 성공 확인
            log("⏳ 로그인 처리 중...")
            page.wait_for_url('**/workspace/**', timeout=15000)
            
            log("✅ 로그인 성공!")
            time.sleep(2)
            
            # 스크린샷 저장
            screenshot_path = SCREENSHOT_DIR / "login_success.png"
            log(f"📸 스크린샷 촬영 중... ({screenshot_path})")
            page.screenshot(path=str(screenshot_path), full_page=False)
            log(f"✅ 스크린샷 저장 완료!")
            
            log("=" * 50)
            log("✅ 모든 테스트 통과!")
            log("=" * 50)
            
            return {
                "success": True,
                "screenshot": "login_success.png",
                "message": "로그인 테스트 성공!"
            }
            
        except Exception as e:
            log(f"❌ 에러 발생: {e}")
            
            # 에러 스크린샷
            try:
                error_screenshot = SCREENSHOT_DIR / "login_error.png"
                page.screenshot(path=str(error_screenshot), full_page=False)
                log(f"📸 에러 스크린샷 저장: {error_screenshot}")
            except:
                pass
            
            return {
                "success": False,
                "screenshot": "login_error.png",
                "message": f"로그인 실패: {str(e)}"
            }
            
        finally:
            if not HEADLESS:
                log("🏁 브라우저를 5초 후 종료합니다...")
                time.sleep(5)
            browser.close()
            log("🏁 테스트 종료")

if __name__ == "__main__":
    test_login_sync()
