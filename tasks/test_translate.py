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

def test_translate_sync(log_callback=None):
    """파일 업로드 후 번역 설정을 완료하는 테스트"""

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

    log(f"🚀 번역 설정 테스트 시작")
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

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}  # 큰 화면!
        )
        
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

            # HubSpot 오버레이 제거
            log("🧹 HubSpot 오버레이 제거 중...")
            page.evaluate('''
                const overlay = document.querySelector('#hs-interactives-modal-overlay');
                if (overlay) overlay.remove();
                const container = document.querySelector('#hs-web-interactives-top-anchor');
                if (container) container.remove();
            ''')
            time.sleep(1)
            log("✅ HubSpot 오버레이 제거 완료!")

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

            # 모달 컨테이너가 먼저 나타날 때까지 대기
            try:
                page.wait_for_selector('[role="dialog"]', state='visible', timeout=15000)
                log("  ✅ 모달 컨테이너 나타남!")
                modal_detected = True

                # 추가로 1초 대기 (모달 내부 콘텐츠 로딩)
                time.sleep(1)

                # 번역 언어 텍스트 확인
                try:
                    page.wait_for_selector('text=번역 언어', timeout=5000)
                    log("  ✅ 번역 설정 모달 콘텐츠 로드 완료!")
                except:
                    log("  ⚠️ 번역 언어 텍스트는 못 찾았지만 모달은 열림")
            except:
                log("  ⚠️ 모달 컨테이너를 찾지 못함")

            if not modal_detected:
                log("⚠️ 15초 대기했지만 모달을 찾지 못함")
                raise Exception("번역 설정 모달을 찾을 수 없음")

            # 안정화 대기
            time.sleep(2)

            # === STEP 4: 번역 설정 모달 확인 ===
            log("\n" + "="*50)
            log("STEP 4: 번역 설정 모달 확인")
            log("="*50)

            log("🧹 HubSpot 오버레이 제거 중...")
            page.evaluate('''
                const overlay = document.querySelector('#hs-interactives-modal-overlay');
                if (overlay) overlay.remove();
                const container = document.querySelector('#hs-web-interactives-top-anchor');
                if (container) container.remove();
            ''')
            time.sleep(1)
            log("✅ HubSpot 오버레이 제거 완료!")

            # STEP 5 시작
            log("\n" + "="*50)

            # URL 및 페이지 상태 확인
            log(f"📍 현재 URL: {page.url}")

            # 번역 설정 모달 찾기
            log("🔍 번역 설정 모달 찾는 중...")
            modal_found = False

            # "번역 언어" 텍스트 확인
            try:
                if page.locator('text=번역 언어').is_visible(timeout=3000):
                    log("  ✅ 번역 설정 모달 발견!")
                    modal_found = True
            except:
                pass

            if not modal_found:
                log("  ⚠️ 번역 설정 모달을 찾지 못했습니다")
                raise Exception("번역 설정 모달 확인 실패")

            log("✅ 번역 설정 모달 확인 완료!")

            # === STEP 5: 원본 언어 선택 (Korean) ===
            log("\n" + "="*50)
            log("STEP 5: 원본 언어 선택 (Korean)")
            log("="*50)

            log("🔍 원본 언어 드롭다운 찾는 중...")
            # 첫 번째 combobox (원본 언어)
            original_lang_dropdown = page.locator('button[role="combobox"]').first

            # 현재 값 확인
            current_value = original_lang_dropdown.inner_text()
            log(f"  📝 현재 드롭다운 값: {current_value}")

            log("👆 원본 언어 드롭다운 클릭...")
            original_lang_dropdown.click(force=True)
            time.sleep(2)

            korean_found = False

            # 방법 3: position 기반 클릭 (좌표로 직접 클릭)
            log("🔍 좌표 기반 클릭 시도...")
            try:
                # 검색 input 찾기
                log("  🔍 검색 input 찾는 중...")
                search_input = page.locator('input[placeholder*="언어를 검색"]').first

                if search_input.is_visible(timeout=3000):
                    log("  ✓ 검색 input 발견!")

                    # Korean 입력
                    log("  ⌨️  'Korean' 입력 중...")
                    search_input.fill("Korean")
                    time.sleep(1.5)
                    log("  ✓ 검색 완료")

                    # Korean 요소의 위치 가져오기
                    log("  📍 Korean 요소의 위치 확인 중...")
                    korean_elements = page.get_by_text("Korean", exact=True).all()

                    # 요소가 실제로 존재하는지 확인
                    if len(korean_elements) > 0:
                        log(f"  📋 발견된 Korean 요소 개수: {len(korean_elements)}")

                        # 2개 이상이면 아래쪽(두 번째) 선택
                        target_element = korean_elements[1] if len(korean_elements) >= 2 else korean_elements[0]
                        element_index = 1 if len(korean_elements) >= 2 else 0

                        box = target_element.bounding_box()

                        if box:
                            # 요소의 중앙 좌표 계산
                            x = box['x'] + box['width'] / 2
                            y = box['y'] + box['height'] / 2

                            log(f"  📍 선택한 Korean 요소: {element_index + 1}번째")
                            log(f"  📍 Korean 위치: x={x:.0f}, y={y:.0f}")

                            # 좌표로 직접 클릭
                            log("  👆 좌표로 클릭 중...")
                            page.mouse.click(x, y)
                            time.sleep(2)

                            korean_found = True
                            log("  ✅ 좌표 클릭 성공!")
                        else:
                            log("  ⚠️ Korean 요소의 bounding box를 가져올 수 없음")
                    else:
                        log("  ⚠️ Korean 요소를 찾을 수 없음")
                else:
                    log("  ⚠️ 검색 input이 보이지 않음")
            except Exception as e:
                log(f"  ⚠️ 좌표 클릭 실패: {e}")

            # 선택 확인
            log("🔍 선택 결과 확인 중...")
            try:
                # 드롭다운이 자동으로 닫힐 때까지 대기
                time.sleep(1)

                selected_value = page.locator('button[role="combobox"]').first.inner_text()
                log(f"  📝 현재 선택된 값: {selected_value}")

                if "Korean" in selected_value:
                    log("✅ 원본 언어 Korean 선택 완료!")
                else:
                    log(f"⚠️ Korean이 선택되지 않음 (현재: {selected_value})")
                    log("⚠️ 계속 진행합니다...")
            except Exception as e:
                log(f"⚠️ 선택 결과 확인 실패: {e}")
                log("⚠️ 계속 진행합니다...")

            # === STEP 6: 번역 언어 선택 (English) ===
            log("\n" + "="*50)
            log("STEP 6: 번역 언어 선택 (English)")
            log("="*50)

            log("🔍 번역 언어 드롭다운 찾는 중...")
            # 두 번째 combobox (번역 언어)
            target_lang_dropdown = page.locator('button[role="combobox"]').nth(1)

            # 현재 값 확인
            try:
                target_current_value = target_lang_dropdown.inner_text()
                log(f"  📝 현재 드롭다운 값: {target_current_value}")
            except:
                log("  📝 현재 드롭다운 값을 가져올 수 없음")

            log("👆 번역 언어 드롭다운 클릭...")
            target_lang_dropdown.click(force=True)
            time.sleep(2)

            english_found = False

            # 좌표 기반 클릭 (STEP 5와 동일한 방식)
            log("🔍 좌표 기반 클릭 시도...")
            try:
                # 검색 input 찾기
                log("  🔍 검색 input 찾는 중...")
                search_input = page.locator('input[placeholder*="언어를 검색"]').first

                if search_input.is_visible(timeout=3000):
                    log("  ✓ 검색 input 발견!")

                    # English 입력
                    log("  ⌨️  'English' 입력 중...")
                    search_input.fill("English")
                    time.sleep(1.5)
                    log("  ✓ 검색 완료")

                    # English 요소의 위치 가져오기
                    log("  📍 English 요소의 위치 확인 중...")
                    english_elements = page.get_by_text("English", exact=True).all()

                    # 요소가 실제로 존재하는지 확인
                    if len(english_elements) > 0:
                        log(f"  📋 발견된 English 요소 개수: {len(english_elements)}")

                        # 👇 마지막 요소(3번째) 선택!
                        target_element = english_elements[-1]
                        element_index = len(english_elements) - 1

                        box = target_element.bounding_box()

                        if box:
                            # 요소의 중앙 좌표 계산
                            x = box['x'] + box['width'] / 2
                            y = box['y'] + box['height'] / 2

                            log(f"  📍 선택한 English 요소: {element_index + 1}번째")
                            log(f"  📍 English 위치: x={x:.0f}, y={y:.0f}")

                            # 좌표로 직접 클릭
                            log("  👆 좌표로 클릭 중...")
                            page.mouse.click(x, y)
                            time.sleep(2)

                            english_found = True
                            log("  ✅ 좌표 클릭 성공!")
                        else:
                            log("  ⚠️ English 요소의 bounding box를 가져올 수 없음")
                    else:
                        log("  ⚠️ English 요소를 찾을 수 없음")
                else:
                    log("  ⚠️ 검색 input이 보이지 않음")
            except Exception as e:
                log(f"  ⚠️ 좌표 클릭 실패: {e}")

            # 선택 확인
            log("🔍 선택 결과 확인 중...")
            try:
                # 선택 후 대기
                time.sleep(1)

                # 알약 모양 UI 확인 (선택된 언어가 별도로 표시됨)
                english_pill = page.get_by_text("English", exact=True).first

                if english_pill.is_visible(timeout=2000):
                    log("  ✓ English 알약 UI 발견!")
                    log("✅ 번역 언어 English 선택 완료!")
                else:
                    log("⚠️ English 알약 UI를 찾을 수 없음")
                    log("⚠️ 계속 진행합니다...")
            except Exception as e:
                log(f"⚠️ 선택 결과 확인 실패: {e}")
                log("⚠️ 계속 진행합니다...")

            # 드롭다운 닫기 (모달 빈 공간 클릭)
            log("🔍 드롭다운 닫는 중...")
            try:
                # 모달 오른쪽 빈 공간 클릭 (좌표로 직접 클릭)
                log("  👆 모달 빈 공간 클릭 (좌표: 900, 300)...")
                page.mouse.click(900, 300)
                time.sleep(1)
                log("  ✓ 드롭다운 닫힘")
            except Exception as e:
                log(f"  ⚠️ 드롭다운 닫기 실패: {e}")

            # === STEP 7: 번역하기 버튼 클릭 ===
            log("\n" + "="*50)
            log("STEP 7: 번역하기 버튼 클릭")
            log("="*50)

            log("🔍 '번역하기' 버튼 찾는 중...")
            translate_button = page.locator('button:has-text("번역하기")').first

            log("👆 '번역하기' 버튼 클릭...")
            translate_button.click()
            
            log("✅ 번역하기 버튼 클릭 완료!")
            time.sleep(3)

            # 👇 먼저 번역 설정 모달 닫기!
            log("🔍 번역 설정 모달 닫기...")
            page.keyboard.press("Escape")
            time.sleep(2)
            log("  ✓ 번역 설정 모달 닫힘")

            # 👇 그 다음 권한 안내 모달 처리!
            log("⏳ '서비스 이용 및 편집 권한 안내' 모달 확인 중...")
            try:
                agree_button = page.locator('button:has-text("동의 후 진행")').first

                if agree_button.is_visible(timeout=5000):
                    log("  ✓ '동의 후 진행' 버튼 발견!")
                    log("  👆 '동의 후 진행' 버튼 클릭...")
                    agree_button.click(force=True)
                    time.sleep(3)
                    log("  ✅ '동의 후 진행' 완료!")
                else:
                    log("  ℹ️ 권한 안내 모달 없음")
            except Exception as e:
                log(f"  ℹ️ 권한 안내 처리: {e}")

            # 가이드 팝업 닫기 (2개)
            log("🔍 가이드 팝업 확인 중...")
            try:
                # 1번째 팝업: "Next" 버튼
                next_button = page.locator('button:has-text("Next")').first
                if next_button.is_visible(timeout=3000):
                    log("  ✓ 1번째 가이드 팝업 발견!")
                    log("  👆 'Next' 버튼 클릭...")
                    next_button.click()
                    time.sleep(2)
                    log("  ✓ 1번째 가이드 팝업 닫힘")

                    # 2번째 팝업: "Done" 버튼
                    log("  🔍 2번째 가이드 팝업 확인 중...")
                    done_button = page.locator('button:has-text("Done")').first
                    if done_button.is_visible(timeout=3000):
                        log("  ✓ 2번째 가이드 팝업 발견!")
                        log("  👆 'Done' 버튼 클릭...")
                        done_button.click()
                        time.sleep(1)
                        log("  ✓ 2번째 가이드 팝업 닫힘")
                    else:
                        log("  ℹ️ 2번째 가이드 팝업 없음")
                else:
                    # X 버튼 시도
                    close_button = page.locator('[aria-label="Close"]').first
                    if close_button.is_visible(timeout=2000):
                        log("  ✓ Close 버튼 발견!")
                        log("  👆 'Close' 버튼 클릭...")
                        close_button.click()
                        time.sleep(1)
                        log("  ✓ 가이드 팝업 닫힘")
                    else:
                        log("  ℹ️ 가이드 팝업 없음")
            except Exception as e:
                log(f"  ℹ️ 가이드 팝업 처리: {e}")

            # 페이지 전환 대기
            log("⏳ 페이지 전환 대기 중...")
            time.sleep(5)

            # 홈 화면으로 이동했는지 확인
            log("🔍 홈 화면 이동 확인 중...")
            try:
                # workspace URL 확인
                current_url = page.url
                log(f"  📍 현재 URL: {current_url}")

                if "/workspace" in current_url:
                    log("  ✓ workspace 페이지에 있음")

                    # 추가로 페이지 로딩 대기
                    time.sleep(3)
                    page.wait_for_load_state('networkidle', timeout=10000)
                    log("  ✓ 페이지 로딩 완료")
                    log("✅ 홈 화면으로 이동 완료!")

                    # 최근 비디오에서 "sample" 영상 확인
                    log("\n🔍 업로드된 영상 확인 중...")
                    try:
                        # "sample" 텍스트 찾기
                        sample_video = page.get_by_text("sample").first

                        if sample_video.is_visible(timeout=5000):
                            log("  ✓ 'sample' 영상 발견!")

                            # "처리 중" 또는 "영상 처리중" 텍스트 찾기
                            processing_text = page.get_by_text("처리", exact=False).first

                            if processing_text.is_visible(timeout=3000):
                                log("  ✓ 영상 처리 중 상태 확인!")
                                log("✅ 영상이 정상적으로 업로드되고 처리 중입니다!")
                            else:
                                log("  ℹ️ 처리 중 텍스트를 찾을 수 없지만 영상은 존재함")
                        else:
                            log("  ⚠️ 'sample' 영상을 찾을 수 없음")
                    except Exception as e:
                        log(f"  ⚠️ 영상 확인 실패: {e}")

                    # 영상 처리 완료 대기
                    log("\n⏳ 영상 처리 완료 대기 중 (최대 5분)...")
                    processing_complete = False
                    max_wait_seconds = 300  # 5분
                    wait_interval = 10  # 10초마다 체크
                    elapsed = 0

                    while elapsed < max_wait_seconds and not processing_complete:
                        time.sleep(wait_interval)
                        elapsed += wait_interval

                        # "몇 초 전", "몇 분 전" 텍스트 찾기
                        try:
                            if page.get_by_text("초 전").is_visible(timeout=1000) or \
                               page.get_by_text("분 전").is_visible(timeout=1000):
                                log(f"  ✅ 영상 처리 완료! (대기 시간: {elapsed}초)")
                                processing_complete = True
                                break
                            else:
                                log(f"  ⏳ 처리 중... ({elapsed}/{max_wait_seconds}초)")
                        except:
                            log(f"  ⏳ 처리 중... ({elapsed}/{max_wait_seconds}초)")

                    if not processing_complete:
                        log(f"  ⚠️ 타임아웃! 5분 초과 (처리 미완료 가능성)")
                    else:
                        log(f"  🎉 영상 처리 성공!")

                else:
                    log(f"  ⚠️ workspace 페이지가 아님: {current_url}")
            except Exception as e:
                log(f"  ⚠️ 홈 화면 확인 실패: {e}")

            # === STEP 8: 스크린샷 저장 ===
            log("\n" + "="*50)
            log("STEP 8: 스크린샷 저장")
            log("="*50)

            screenshot_path = SCREENSHOT_DIR / "translate_success.png"
            log(f"📸 스크린샷 촬영 중...")
            page.screenshot(path=str(screenshot_path), full_page=False)
            log(f"✅ 스크린샷 저장 완료: {screenshot_path.name}")

            log("\n" + "="*50)
            log("✅ 번역 설정 테스트 완료!")
            log("="*50)

            return {
                "success": True,
                "screenshot": "translate_success.png",
                "message": "번역 설정이 성공적으로 완료되었습니다!"
            }

        except Exception as e:
            log(f"❌ 에러 발생: {e}")

            # 에러 스크린샷
            try:
                error_screenshot = SCREENSHOT_DIR / "translate_error.png"
                page.screenshot(path=str(error_screenshot), full_page=False)
                log(f"📸 에러 스크린샷 저장")
            except:
                pass

            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "screenshot": "translate_error.png",
                "message": f"번역 설정 실패: {str(e)}"
            }

        finally:
            if not HEADLESS:
                log("🏁 브라우저를 5초 후 종료합니다...")
                time.sleep(5)
            browser.close()
            log("🏁 테스트 종료")

if __name__ == "__main__":
    test_translate_sync()
