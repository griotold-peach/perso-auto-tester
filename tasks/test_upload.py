import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import PERSO_EMAIL, HEADLESS, SCREENSHOT_DIR, VIDEO_FILE_PATH
from utils.login import do_login
from utils.upload import upload_file
from utils.popup_handler import accept_cookies, close_hubspot_iframe_popup, close_all_popups, remove_hubspot_overlay
from utils.browser import create_browser_context
from utils.logger import create_logger

def test_upload_sync(log_callback=None):
    """파일 업로드 테스트 (번역 설정 모달 나타나는지까지)"""

    log = create_logger(log_callback)

    log(f"🚀 업로드 테스트 시작")
    log(f"📧 이메일: {PERSO_EMAIL}")
    log(f"🎬 영상 파일: {VIDEO_FILE_PATH}")
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

            # 쿠키 수락
            try:
                accept_cookies(page)
            except Exception as e:
                log(f"  ⚠️ 쿠키 수락 실패: {e}")

            # HubSpot iframe 팝업
            try:
                close_hubspot_iframe_popup(page)
            except Exception as e:
                log(f"  ⚠️ HubSpot 팝업 실패: {e}")

            # HubSpot 오버레이 제거
            remove_hubspot_overlay(page, log)

            # 모든 팝업 닫기
            try:
                close_all_popups(page)
            except Exception as e:
                log(f"  ⚠️ 팝업 닫기 실패: {e}")

            # 페이지 맨 위로 스크롤
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            log("✅ 팝업/모달 정리 완료")
            
            # === STEP 3: 파일 업로드 ===
            log("\n" + "="*50)
            log("STEP 3: 파일 업로드")
            log("="*50)

            modal_detected = upload_file(page, log)

            # upload_file에서 모달을 찾지 못한 경우 실패 처리
            if not modal_detected:
                log("\n" + "="*50)
                log("❌ 테스트 실패: 번역 설정 모달을 찾을 수 없음")
                log("="*50)

                # 에러 스크린샷
                try:
                    error_screenshot = SCREENSHOT_DIR / "upload_error.png"
                    page.screenshot(path=str(error_screenshot), full_page=False)
                    log(f"📸 에러 스크린샷 저장")
                except:
                    pass

                return {
                    "success": False,
                    "screenshot": "upload_error.png",
                    "message": "번역 설정 모달을 찾을 수 없음"
                }

            # === STEP 4: 번역 설정 모달 확인 ===
            log("\n" + "="*50)
            log("STEP 4: 번역 설정 모달 확인")
            log("="*50)

            # 번역 설정 모달 재확인
            log("🔍 번역 설정 모달 재확인 중...")
            modal_found = False

            # 방법 1: "번역 언어" 텍스트
            try:
                if page.locator('text=번역 언어').is_visible(timeout=3000):
                    log("  ✅ 번역 설정 모달 발견 (번역 언어 텍스트)")
                    modal_found = True
            except:
                pass

            # 방법 2: "Auto Detect" 텍스트
            if not modal_found:
                try:
                    if page.locator('text=Auto Detect').is_visible(timeout=3000):
                        log("  ✅ 번역 설정 모달 발견 (Auto Detect)")
                        modal_found = True
                except:
                    pass

            # 방법 3: "언어 선택" 버튼
            if not modal_found:
                try:
                    if page.locator('button:has-text("언어 선택")').is_visible(timeout=3000):
                        log("  ✅ 번역 설정 모달 발견 (언어 선택 버튼)")
                        modal_found = True
                except:
                    pass

            if not modal_found:
                log("  ⚠️ 번역 설정 모달을 찾지 못했습니다")

                # URL 및 페이지 상태 확인
                log(f"📍 현재 URL: {page.url}")
                try:
                    page_info = page.evaluate('''
                        () => {
                            return {
                                url: window.location.href,
                                readyState: document.readyState,
                                title: document.title,
                                bodyInnerText: document.body.innerText.substring(0, 200)
                            };
                        }
                    ''')
                    log(f"  📄 페이지 제목: {page_info.get('title', 'N/A')}")
                    log(f"  🔄 ReadyState: {page_info.get('readyState', 'N/A')}")
                    log(f"  📝 페이지 내용 (앞 200자): {page_info.get('bodyInnerText', 'N/A')[:100]}...")
                except Exception as e:
                    log(f"  ⚠️ 페이지 정보 확인 실패: {e}")

                # 보이는 버튼들 출력
                log("  💡 현재 페이지 상태 확인 중...")
                try:
                    buttons = page.locator('button:visible').all()
                    log(f"  📋 보이는 버튼 개수: {len(buttons)}")
                    for i, btn in enumerate(buttons[:10]):
                        try:
                            text = btn.inner_text(timeout=500).strip()
                            if text:
                                log(f"     {i+1}. '{text}'")
                        except:
                            pass
                except Exception as e:
                    log(f"  ⚠️ 버튼 확인 실패: {e}")
            else:
                log("✅ 번역 설정 모달 확인 완료!")
            
            # 스크린샷 저장
            screenshot_path = SCREENSHOT_DIR / "upload_modal.png"
            log(f"📸 스크린샷 촬영 중...")
            page.screenshot(path=str(screenshot_path), full_page=False)
            log(f"✅ 스크린샷 저장 완료!")
            
            log("\n" + "="*50)
            log("✅ 업로드 테스트 완료!")
            log("="*50)
            
            if modal_found:
                message = "업로드 성공! 번역 설정 모달이 나타났습니다."
            else:
                message = "업로드 완료했지만 번역 설정 모달을 찾지 못했습니다."
            
            return {
                "success": modal_found,
                "screenshot": "upload_modal.png",
                "message": message
            }
            
        except Exception as e:
            log(f"❌ 에러 발생: {e}")
            
            # 에러 스크린샷
            try:
                error_screenshot = SCREENSHOT_DIR / "upload_error.png"
                page.screenshot(path=str(error_screenshot), full_page=False)
                log(f"📸 에러 스크린샷 저장")
            except:
                pass
            
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "screenshot": "upload_error.png",
                "message": f"업로드 실패: {str(e)}"
            }
            
        finally:
            if not HEADLESS:
                log("🏁 브라우저를 5초 후 종료합니다...")
                time.sleep(5)
            browser.close()
            log("🏁 테스트 종료")

if __name__ == "__main__":
    test_upload_sync()
