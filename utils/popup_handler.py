import time

def accept_cookies(page):
    """쿠키 수락 처리"""
    print("🍪 쿠키 배너 확인 중...")

    try:
        cookie_button_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Accept all")',
            'button:has-text("수락")',
            'button:has-text("모두 수락")',
            'button:has-text("동의")',
            'button:has-text("모두 동의")',
        ]

        for selector in cookie_button_selectors:
            try:
                button = page.locator(selector).first
                if button.is_visible(timeout=2000):
                    button.click(force=True)
                    print(f"✅ 쿠키 수락 완료")
                    time.sleep(1)
                    return True
            except:
                continue

        print("ℹ️  쿠키 배너 없음")
        return False

    except Exception as e:
        print(f"⚠️  쿠키 처리 중 에러: {e}")
        return False

def close_hubspot_iframe_popup(page):
    """HubSpot iframe 팝업 닫기"""
    print("🔍 HubSpot iframe 팝업 확인 중...")
    
    try:
        # iframe 자체를 강제로 제거
        page.evaluate('''
            const iframes = document.querySelectorAll('iframe[title*="Popup"], iframe[id*="hs-"]');
            iframes.forEach(iframe => {
                if (iframe.parentElement) {
                    iframe.parentElement.remove();
                } else {
                    iframe.remove();
                }
            });
        ''')
        print("✅ HubSpot iframe 제거")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"ℹ️  HubSpot iframe 없음: {e}")
        return False

def close_all_popups(page):
    """모든 팝업/모달/오버레이 닫기"""
    print("🔍 모든 팝업/오버레이 확인 중...")
    
    closed_count = 0
    max_attempts = 5
    
    for attempt in range(max_attempts):
        found_close_button = False
        
        # X 버튼 찾기
        close_selectors = [
            'button:has-text("×")',
            'button:has-text("✕")',
            'button[aria-label="Close"]',
            'button[aria-label="close"]',
        ]
        
        for selector in close_selectors:
            try:
                buttons = page.locator(selector)
                count = buttons.count()
                
                if count > 0:
                    for i in range(count):
                        button = buttons.nth(i)
                        try:
                            if button.is_visible(timeout=1000):
                                box = button.bounding_box()
                                if box and box['width'] < 50 and box['height'] < 50:
                                    button.click(force=True, timeout=3000)
                                    closed_count += 1
                                    found_close_button = True
                                    print(f"✅ 팝업 {closed_count}개 닫음")
                                    time.sleep(1)
                                    break
                        except:
                            continue
                
                if found_close_button:
                    break
                    
            except:
                continue
        
        if not found_close_button:
            break
        
        time.sleep(0.5)
    
    if closed_count > 0:
        print(f"✅ 총 {closed_count}개의 팝업을 닫았습니다")
    else:
        print("ℹ️  닫을 팝업이 없습니다")

    return closed_count > 0

def remove_hubspot_overlay(page, log=None):
    """HubSpot 오버레이 제거

    Args:
        page: Playwright page 객체
        log: 로그 출력 함수 (optional)

    Returns:
        bool: 제거 성공 여부
    """
    if log:
        log("🧹 HubSpot 오버레이 제거 중...")
    else:
        print("🧹 HubSpot 오버레이 제거 중...")

    try:
        page.evaluate('''
            const overlay = document.querySelector('#hs-interactives-modal-overlay');
            if (overlay) overlay.remove();
            const container = document.querySelector('#hs-web-interactives-top-anchor');
            if (container) container.remove();
        ''')
        time.sleep(1)

        if log:
            log("✅ HubSpot 오버레이 제거 완료!")
        else:
            print("✅ HubSpot 오버레이 제거 완료!")

        return True
    except Exception as e:
        if log:
            log(f"⚠️ HubSpot 오버레이 제거 실패: {e}")
        else:
            print(f"⚠️ HubSpot 오버레이 제거 실패: {e}")

        return False

def close_all_modals_and_popups(page, log=None):
    """모든 팝업/모달/오버레이 한 번에 정리
    
    Args:
        page: Playwright page 객체
        log: 로그 출력 함수 (optional)
    
    Returns:
        None
    """
    def _log(msg):
        if log:
            log(msg)
        else:
            print(msg)
    
    _log("🧹 팝업/모달 정리 시작...")
    
    # 1. 쿠키 수락
    try:
        accept_cookies(page)
    except Exception as e:
        _log(f"  ⚠️ 쿠키 수락 실패: {e}")
    
    # 2. HubSpot iframe 제거
    try:
        close_hubspot_iframe_popup(page)
    except Exception as e:
        _log(f"  ⚠️ HubSpot iframe 실패: {e}")
    
    # 3. HubSpot 오버레이 제거
    try:
        remove_hubspot_overlay(page, _log)
    except Exception as e:
        _log(f"  ⚠️ HubSpot 오버레이 실패: {e}")
    
    # 4. 모든 팝업 닫기
    try:
        close_all_popups(page)
    except Exception as e:
        _log(f"  ⚠️ 팝업 닫기 실패: {e}")
    
    # 5. 맨 위로 스크롤
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    
    _log("✅ 팝업/모달 정리 완료!")