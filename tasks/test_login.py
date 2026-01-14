import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import PERSO_EMAIL, HEADLESS, SCREENSHOT_DIR
from utils.browser import create_browser_context
from utils.login import do_login
from utils.popup_handler import close_all_modals_and_popups
from utils.logger import create_logger
from utils.verification import verify_login_success

def test_login_sync(log_callback=None):
    """로그인 테스트"""
    
    log = create_logger(log_callback)
    
    log(f"🚀 로그인 테스트 시작")
    log(f"📧 이메일: {PERSO_EMAIL}")
    log(f"🖥️  Headless: {HEADLESS}")
    
    with sync_playwright() as p:
        # 브라우저 컨텍스트 생성 (utils.browser 사용)
        browser, context, page = create_browser_context(p, headless=HEADLESS)
        
        try:
            # === STEP 1: 로그인 ===
            log("\n" + "="*50)
            log("STEP 1: 로그인")
            log("="*50)

            do_login(page, log)

            # === STEP 2: 팝업/모달 닫기 ===
            log("\n" + "="*50)
            log("STEP 2: 팝업/모달 닫기")
            log("="*50)

            close_all_modals_and_popups(page, log) 

            # STEP 3: 로그인 성공 확인
            log("\n" + "="*50)
            log("STEP 3: 로그인 성공 확인")
            log("="*50)
            
            try:
                verify_login_success(page, log)
            except Exception as e:
                # 에러 스크린샷
                error_screenshot = SCREENSHOT_DIR / "login_error.png"
                page.screenshot(path=str(error_screenshot))
                
                return {
                    "success": False,
                    "screenshot": "login_error.png",
                    "message": f"로그인 검증 실패: {e}"
                }

            # === STEP 4: 스크린샷 저장 (드롭다운 열린 상태) ===
            log("\n" + "="*50)
            log("STEP 4: 스크린샷 저장")
            log("="*50)

            screenshot_path = SCREENSHOT_DIR / "login_success.png"
            log(f"📸 스크린샷 촬영 중 (드롭다운 열린 상태)...")
            page.screenshot(path=str(screenshot_path), full_page=False)
            log(f"✅ 스크린샷 저장 완료: {screenshot_path.name}")

            # 드롭다운 닫기
            log("🔽 드롭다운 닫는 중...")
            page.keyboard.press('Escape')
            time.sleep(0.5)

            log("\n" + "="*50)
            log("✅ 로그인 테스트 완료!")
            log("="*50)

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
                log(f"📸 에러 스크린샷 저장")
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
