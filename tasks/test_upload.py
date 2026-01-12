import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
import asyncio

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import PERSO_EMAIL, PERSO_PASSWORD, HEADLESS, SCREENSHOT_DIR, VIDEO_FILE_PATH
from utils.popup_handler import accept_cookies, close_hubspot_iframe_popup, close_all_popups

def test_upload_sync(log_callback=None):
    """파일 업로드 테스트 (번역 설정 모달 나타나는지까지)"""
    
    def log(msg):
        """로그 출력 및 콜백 호출"""
        print(msg)
        if log_callback:
            if asyncio.iscoroutinefunction(log_callback):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(log_callback(msg))
                except:
                    pass
            else:
                log_callback(msg)
    
    log(f"🚀 업로드 테스트 시작")
    log(f"📧 이메일: {PERSO_EMAIL}")
    log(f"🎬 영상 파일: {VIDEO_FILE_PATH}")
    log(f"🖥️  Headless: {HEADLESS}")
    
    with sync_playwright() as p:
        # 브라우저 설정
        launch_options = {'headless': HEADLESS}
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
            # === STEP 1: 로그인 ===
            log("\n" + "="*50)
            log("STEP 1: 로그인")
            log("="*50)
            
            log("📍 로그인 페이지 접속 중...")
            page.goto('https://perso.ai/ko/login', timeout=30000)
            page.wait_for_load_state('networkidle')
            
            log("📝 이메일 입력 중...")
            email_input = page.locator('input[type="email"], input[placeholder*="이메일"]')
            email_input.fill(PERSO_EMAIL)
            time.sleep(0.5)
            
            log("👆 계속 버튼 클릭...")
            continue_button = page.locator('button:has-text("계속")')
            continue_button.click()
            time.sleep(2)
            
            log("🔐 비밀번호 입력 중...")
            password_input = page.locator('input[type="password"]')
            password_input.fill(PERSO_PASSWORD)
            time.sleep(0.5)
            
            log("🚪 Enter 키로 로그인 제출...")
            password_input.press('Enter')
            
            log("⏳ 로그인 처리 중...")
            page.wait_for_url('**/workspace/**', timeout=15000)
            log("✅ 로그인 성공!")
            
            # 화면 로딩 대기
            log("⏳ 페이지 로딩 대기 중...")
            try:
                page.wait_for_load_state('networkidle', timeout=10000)
                log("  ✓ 네트워크 로딩 완료")
            except:
                log("  ⚠️ 네트워크 타임아웃")
            
            time.sleep(2)
            
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

            log("📁 파일 input 찾는 중...")
            file_input = page.locator('input[type="file"]').first

            if not file_input.count():
                log("❌ 파일 input을 찾을 수 없습니다")
                raise Exception("파일 input 없음")

            log(f"📤 파일 업로드 중: {Path(VIDEO_FILE_PATH).name}")
            file_input.set_input_files(VIDEO_FILE_PATH)
            log("  ✓ 파일 선택 완료")

            # 번역 설정 모달 대기
            log("⏳ 번역 설정 모달 대기 중...")
            modal_detected = False

            # 1단계: 모달 컨테이너가 먼저 나타날 때까지 대기
            try:
                page.wait_for_selector('[role="dialog"]', state='visible', timeout=15000)
                log("  ✅ 모달 컨테이너 나타남!")
                modal_detected = True

                # 추가로 1초 대기 (모달 내부 콘텐츠 로딩)
                time.sleep(1)

                # 2단계: 번역 언어 텍스트 확인
                try:
                    page.wait_for_selector('text=번역 언어', timeout=5000)
                    log("  ✅ 번역 설정 모달 콘텐츠 로드 완료!")
                except:
                    log("  ⚠️ 번역 언어 텍스트는 못 찾았지만 모달은 열림")
            except:
                log("  ⚠️ 모달 컨테이너를 찾지 못함")

            if not modal_detected:
                log("⚠️ 15초 대기했지만 모달을 찾지 못함")

            # 안정화 대기
            time.sleep(2)
            
            # === STEP 4: 번역 설정 모달 확인 ===
            log("\n" + "="*50)
            log("STEP 4: 번역 설정 모달 확인")
            log("="*50)

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

            # 방해 요소 제거
            # log("🧹 방해 요소 제거 중...")
            # page.evaluate('''
            #     // iframe 모두 제거
            #     document.querySelectorAll('iframe').forEach(iframe => {
            #         if (iframe.parentElement) {
            #             iframe.parentElement.remove();
            #         } else {
            #             iframe.remove();
            #         }
            #     });
            #
            #     // 오버레이 제거
            #     document.querySelectorAll('[data-state="open"][aria-hidden="true"]').forEach(el => el.remove());
            #
            #     // HubSpot 제거
            #     document.querySelectorAll('[id*="hs-"], [class*="hs-"]').forEach(elem => {
            #         if (elem.tagName === 'DIV' || elem.tagName === 'IFRAME') {
            #             elem.remove();
            #         }
            #     });
            # ''')
            # time.sleep(1)

            # 번역 설정 모달 찾기
            log("🔍 번역 설정 모달 찾는 중...")
            modal_found = False

            # ... (나머지 코드 동일)
            
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
                log("  💡 현재 페이지 상태 확인 중...")
                
                # 보이는 버튼들 출력
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
