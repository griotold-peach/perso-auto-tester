"""테스트 검증 유틸리티"""
import time


def verify_login_success(page, log):
    """로그인 성공 여부 검증
    
    프로필 드롭다운 → 로그아웃 버튼 확인
    
    Args:
        page: Playwright page
        log: 로그 함수
        
    Returns:
        bool: 검증 성공 여부
        
    Raises:
        Exception: 검증 실패 시
    """
    log("🔍 로그인 성공 여부 확인 중...")
    time.sleep(2)  # 화면 안정화
    
    # 1. 프로필 버튼 찾기
    log("  🔍 프로필 버튼 검색 중...")
    try:
        profile_button = page.locator('text=Plan').first
        if not profile_button.is_visible(timeout=3000):
            raise Exception("프로필 버튼을 찾을 수 없음")
        log("  ✅ 프로필 버튼 발견!")
    except Exception as e:
        log(f"  ❌ 프로필 버튼 검색 실패: {e}")
        raise
    
    # 2. 드롭다운 열기
    log("  👆 프로필 드롭다운 클릭...")
    profile_button.click()
    time.sleep(2)  # 드롭다운 애니메이션 대기
    
    # 3. 로그아웃 버튼 확인
    log("  🔍 로그아웃 버튼 검색 중...")
    try:
        logout_button = page.locator('text=로그아웃').first
        if not logout_button.is_visible(timeout=3000):
            raise Exception("로그아웃 버튼을 찾을 수 없음")
        log("  ✅ 로그아웃 버튼 발견!")
    except Exception as e:
        log(f"  ❌ 로그아웃 버튼 검색 실패: {e}")
        raise
    
    log("✅ 로그인 성공 확인 완료!")
    return True


def verify_upload_success(page, log):
    """업로드 성공 여부 검증
    
    번역 설정 모달 확인
    
    Args:
        page: Playwright page
        log: 로그 함수
        
    Returns:
        bool: 검증 성공 여부
        
    Raises:
        Exception: 검증 실패 시
    """
    log("🔍 업로드 성공 여부 확인 중...")
    
    # 번역 설정 모달 확인
    log("  🔍 번역 설정 모달 검색 중...")
    try:
        modal = page.get_by_text("번역 설정", exact=False).first
        if not modal.is_visible(timeout=5000):
            raise Exception("번역 설정 모달을 찾을 수 없음")
        log("  ✅ 번역 설정 모달 발견!")
    except Exception as e:
        log(f"  ❌ 모달 검색 실패: {e}")
        raise
    
    log("✅ 업로드 성공 확인 완료!")
    return True


def verify_translate_success(page, log):
    """번역 성공 여부 검증
    
    sample 영상의 처리 완료 상태 확인
    
    Args:
        page: Playwright page
        log: 로그 함수
        
    Returns:
        bool: 검증 성공 여부
        
    Raises:
        Exception: 검증 실패 시
    """
    log("🔍 번역 성공 여부 확인 중...")
    
    # sample 영상 찾기
    log("  🔍 sample 영상 검색 중...")
    try:
        sample_video = page.get_by_text("sample", exact=False).first
        if not sample_video.is_visible(timeout=5000):
            raise Exception("sample 영상을 찾을 수 없음")
        log("  ✅ sample 영상 발견!")
    except Exception as e:
        log(f"  ❌ 영상 검색 실패: {e}")
        raise
    
    # 처리 완료 확인 ("초 전" / "분 전")
    log("  🔍 처리 완료 상태 확인 중...")
    
    # 처리 중 상태 체크
    processing_indicators = ["대기 중", "영상 처리 중", "음성 추출 중", "번역 중", "음성 생성 중"]
    
    max_wait_time = 600  # 10분
    elapsed = 0
    check_interval = 30  # 30초마다
    
    while elapsed < max_wait_time:
        # Failed 체크
        try:
            failed_elem = page.get_by_text("Failed", exact=False).first
            if failed_elem.is_visible(timeout=1000):
                log("  ❌ Failed 발견!")
                raise Exception("영상 처리 실패 (Failed)")
        except:
            pass
        
        # 완료 체크 ("초 전" / "분 전")
        try:
            time_ago = page.locator('text=/[0-9]+초 전|[0-9]+분 전/').first
            if time_ago.is_visible(timeout=1000):
                log(f"  ✅ 처리 완료! (대기 시간: {elapsed}초)")
                log("✅ 번역 성공 확인 완료!")
                return True
        except:
            pass
        
        # 처리 중 체크
        processing = False
        for indicator in processing_indicators:
            try:
                elem = page.get_by_text(indicator, exact=False).first
                if elem.is_visible(timeout=500):
                    log(f"  ⏳ {indicator} (대기: {elapsed}/{max_wait_time}초)")
                    processing = True
                    break
            except:
                continue
        
        if not processing:
            # 처리 중도 아니고 완료도 아님 → 알 수 없는 상태
            log(f"  ⚠️ 알 수 없는 상태 (대기: {elapsed}초)")
        
        # 30초 대기
        time.sleep(check_interval)
        elapsed += check_interval
    
    # 타임아웃
    raise Exception(f"처리 완료 타임아웃 ({max_wait_time}초 초과)")