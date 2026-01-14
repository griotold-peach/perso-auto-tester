import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
import asyncio

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import PERSO_EMAIL, HEADLESS, SCREENSHOT_DIR
from utils.browser import create_browser_context
from utils.login import do_login
from utils.popup_handler import accept_cookies, close_hubspot_iframe_popup, close_all_popups, remove_hubspot_overlay

def test_login_sync(log_callback=None):
    """로그인 테스트 (동기 버전)"""
    
    def log(msg):
        """로그 출력 및 콜백 호출"""
        print(msg)
        if log_callback:
            if asyncio.iscoroutinefunction(log_callback):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(log_callback(msg))
                    else:
                        asyncio.run(log_callback(msg))
                except:
                    pass
            else:
                log_callback(msg)
    
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

            # === STEP 3: 로그인 성공 확인 (프로필 드롭다운 → 로그아웃 버튼) ===
            log("\n" + "="*50)
            log("STEP 3: 로그인 성공 확인")
            log("="*50)

            log("🔍 프로필 드롭다운 찾는 중...")

            # 추가 대기 시간 (화면 완전히 로드)
            log("  ⏳ 화면 안정화 대기 중...")
            time.sleep(2)

            profile_button = None
            profile_info = {}  # 클릭한 요소 정보 저장

            try:
                # === "Plan" 키워드로 프로필 버튼 찾기 ===
                log("  🔍 'Plan' 키워드로 프로필 버튼 검색 중...")

                # 방법 1: text=Plan (정확히 "Plan"이 포함된 요소)
                plan_elements = page.locator('text=Plan').all()
                log(f"  📊 'Plan' 텍스트를 포함한 요소: {len(plan_elements)}개 발견")

                plan_candidates = []
                for i, elem in enumerate(plan_elements):
                    try:
                        if elem.is_visible(timeout=500):
                            box = elem.bounding_box()
                            text = elem.inner_text(timeout=500).strip()
                            tag_name = elem.evaluate("el => el.tagName.toLowerCase()")
                            class_name = elem.get_attribute("class") or ""

                            plan_candidates.append({
                                'elem': elem,
                                'text': text,
                                'x': box['x'],
                                'y': box['y'],
                                'width': box['width'],
                                'height': box['height'],
                                'tag': tag_name,
                                'class': class_name
                            })

                            log(f"    {i+1}. <{tag_name}> '{text[:50]}' at ({box['x']:.0f}, {box['y']:.0f}) size=({box['width']:.0f}x{box['height']:.0f})")
                    except Exception as e:
                        log(f"    ⚠️ {i+1}번째 요소 처리 실패: {e}")

                # 방법 2: get_by_text("Plan")도 시도
                if not plan_candidates:
                    log("  🔍 get_by_text('Plan')로 재검색 중...")
                    try:
                        plan_by_text = page.get_by_text("Plan", exact=False)
                        count = plan_by_text.count()
                        log(f"  📊 get_by_text로 {count}개 발견")

                        for i in range(count):
                            try:
                                elem = plan_by_text.nth(i)
                                if elem.is_visible(timeout=500):
                                    box = elem.bounding_box()
                                    text = elem.inner_text(timeout=500).strip()
                                    tag_name = elem.evaluate("el => el.tagName.toLowerCase()")
                                    class_name = elem.get_attribute("class") or ""

                                    plan_candidates.append({
                                        'elem': elem,
                                        'text': text,
                                        'x': box['x'],
                                        'y': box['y'],
                                        'width': box['width'],
                                        'height': box['height'],
                                        'tag': tag_name,
                                        'class': class_name
                                    })

                                    log(f"    {i+1}. <{tag_name}> '{text[:50]}' at ({box['x']:.0f}, {box['y']:.0f}) size=({box['width']:.0f}x{box['height']:.0f})")
                            except Exception as e:
                                log(f"    ⚠️ {i+1}번째 요소 처리 실패: {e}")
                    except Exception as e:
                        log(f"  ⚠️ get_by_text 실패: {e}")

                # 프로필 버튼 선택: 클릭 가능한 첫 번째 요소 선택
                if plan_candidates:
                    log(f"  📋 총 {len(plan_candidates)}개의 'Plan' 후보 발견")

                    # 클릭 가능한 요소인지 확인 (button, a, div[role="button"] 등)
                    clickable_candidates = []
                    for cand in plan_candidates:
                        # 부모 요소가 클릭 가능한지 확인
                        try:
                            # 현재 요소가 버튼이거나 링크인 경우
                            if cand['tag'] in ['button', 'a']:
                                clickable_candidates.append(cand)
                            else:
                                # 부모 요소 중 클릭 가능한 요소 찾기
                                parent_button = cand['elem'].locator('xpath=ancestor::button[1] | ancestor::a[1] | ancestor::div[@role="button"][1]').first
                                if parent_button.count() > 0:
                                    box = parent_button.bounding_box()
                                    text = parent_button.inner_text(timeout=500).strip()
                                    tag_name = parent_button.evaluate("el => el.tagName.toLowerCase()")
                                    class_name = parent_button.get_attribute("class") or ""

                                    clickable_candidates.append({
                                        'elem': parent_button,
                                        'text': text,
                                        'x': box['x'],
                                        'y': box['y'],
                                        'width': box['width'],
                                        'height': box['height'],
                                        'tag': tag_name,
                                        'class': class_name
                                    })
                                else:
                                    # 부모가 없으면 현재 요소 그대로 사용
                                    clickable_candidates.append(cand)
                        except:
                            clickable_candidates.append(cand)

                    log(f"  📋 클릭 가능한 후보: {len(clickable_candidates)}개")

                    if clickable_candidates:
                        # 첫 번째 후보 선택
                        best = clickable_candidates[0]
                        profile_button = best['elem']
                        profile_info = {
                            'text': best['text'],
                            'position': f"({best['x']:.0f}, {best['y']:.0f})",
                            'size': f"{best['width']:.0f}x{best['height']:.0f}",
                            'tag': best['tag'],
                            'class': best['class'][:50] if best['class'] else 'N/A'
                        }

                        log(f"  ✅ 프로필 버튼 선택됨:")
                        log(f"     • 태그: <{profile_info['tag']}>")
                        log(f"     • 텍스트: '{profile_info['text'][:50]}'")
                        log(f"     • 위치: {profile_info['position']}")
                        log(f"     • 크기: {profile_info['size']}")
                        log(f"     • 클래스: {profile_info['class']}")
                else:
                    log("  ⚠️ 'Plan' 키워드를 포함한 요소를 찾지 못했습니다")

            except Exception as e:
                log(f"  ❌ 프로필 버튼 검색 중 에러: {e}")
                import traceback
                log(f"  상세: {traceback.format_exc()}")

            if not profile_button:
                log("\n" + "="*50)
                log("❌ 테스트 실패: 프로필 버튼을 찾을 수 없음")
                log("="*50)

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
                    "message": "프로필 버튼을 찾을 수 없음"
                }

            # 프로필 드롭다운 클릭
            log("  👆 프로필 드롭다운 클릭 중...")
            if profile_info:
                log(f"     클릭할 요소: <{profile_info['tag']}> '{profile_info['text'][:30]}' at {profile_info['position']}")
            profile_button.click()
            log("  ✅ 클릭 완료!")

            # 드롭다운 애니메이션 완료 대기
            log("  ⏳ 드롭다운 메뉴 로딩 대기 중...")
            time.sleep(2)

            # 드롭다운 열린 후 스크린샷 (디버깅용)
            try:
                dropdown_screenshot = SCREENSHOT_DIR / "login_dropdown.png"
                page.screenshot(path=str(dropdown_screenshot), full_page=False)
                log(f"  📸 드롭다운 스크린샷 저장: {dropdown_screenshot.name}")
            except Exception as e:
                log(f"  ⚠️ 드롭다운 스크린샷 저장 실패: {e}")

            # "로그아웃" 버튼 확인
            log("  🔍 로그아웃 버튼 확인 중...")
            logout_found = False
            logout_button = None

            try:
                # 방법 1: text=로그아웃
                log("    🔍 방법 1: text=로그아웃")
                try:
                    logout_loc = page.locator('text=로그아웃')
                    count = logout_loc.count()
                    log(f"      📊 {count}개 발견")

                    if count > 0:
                        for i in range(count):
                            elem = logout_loc.nth(i)
                            if elem.is_visible(timeout=1000):
                                logout_button = elem
                                logout_found = True
                                log(f"      ✅ 로그아웃 버튼 발견 (text=로그아웃, {i+1}번째)")
                                break
                except Exception as e:
                    log(f"      ⚠️ 실패: {e}")

                # 방법 2: button:has-text("로그아웃")
                if not logout_found:
                    log("    🔍 방법 2: button:has-text(\"로그아웃\")")
                    try:
                        logout_button_loc = page.locator('button:has-text("로그아웃")')
                        count = logout_button_loc.count()
                        log(f"      📊 {count}개 발견")

                        if count > 0:
                            elem = logout_button_loc.first
                            if elem.is_visible(timeout=1000):
                                logout_button = elem
                                logout_found = True
                                log(f"      ✅ 로그아웃 버튼 발견 (button:has-text)")
                    except Exception as e:
                        log(f"      ⚠️ 실패: {e}")

                # 방법 3: a:has-text("로그아웃")
                if not logout_found:
                    log("    🔍 방법 3: a:has-text(\"로그아웃\")")
                    try:
                        logout_link_loc = page.locator('a:has-text("로그아웃")')
                        count = logout_link_loc.count()
                        log(f"      📊 {count}개 발견")

                        if count > 0:
                            elem = logout_link_loc.first
                            if elem.is_visible(timeout=1000):
                                logout_button = elem
                                logout_found = True
                                log(f"      ✅ 로그아웃 버튼 발견 (a:has-text)")
                    except Exception as e:
                        log(f"      ⚠️ 실패: {e}")

                # 방법 4: get_by_text로 검색
                if not logout_found:
                    log("    🔍 방법 4: get_by_text(\"로그아웃\")")
                    try:
                        logout_by_text = page.get_by_text("로그아웃", exact=False)
                        count = logout_by_text.count()
                        log(f"      📊 {count}개 발견")

                        if count > 0:
                            for i in range(count):
                                elem = logout_by_text.nth(i)
                                if elem.is_visible(timeout=500):
                                    logout_button = elem
                                    logout_found = True
                                    log(f"      ✅ 로그아웃 버튼 발견 (get_by_text, {i+1}번째)")
                                    break
                    except Exception as e:
                        log(f"      ⚠️ 실패: {e}")

                # 디버깅: 현재 보이는 모든 버튼/링크 출력
                if not logout_found:
                    log("    🔍 디버깅: 현재 보이는 모든 텍스트 요소 확인")
                    try:
                        # 모든 보이는 버튼
                        visible_buttons = page.locator('button:visible, a:visible, [role="button"]:visible').all()
                        log(f"      📋 보이는 클릭 가능 요소 {len(visible_buttons)}개:")

                        for i, btn in enumerate(visible_buttons[:15]):
                            try:
                                text = btn.inner_text(timeout=300).strip()
                                if text:
                                    log(f"        {i+1}. '{text[:50]}'")
                            except:
                                pass
                    except Exception as e:
                        log(f"      ⚠️ 버튼 목록 확인 실패: {e}")

            except Exception as e:
                log(f"  ❌ 로그아웃 버튼 검색 중 에러: {e}")
                import traceback
                log(f"  상세: {traceback.format_exc()}")

            if not logout_found:
                log("\n" + "="*50)
                log("❌ 테스트 실패: 로그아웃 버튼을 찾을 수 없음")
                log("="*50)

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
                    "message": "로그아웃 버튼을 찾을 수 없음"
                }

            log("  ✅ 로그아웃 버튼 확인 완료!")
            log("✅ 로그인 성공 확인 완료!")

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
