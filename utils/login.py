import time

async def login(page, email, password, log_callback=None):
    """PERSO AI 로그인 공통 함수"""
    
    async def log(msg):
        if log_callback:
            await log_callback(msg)
        print(msg)
    
    await log("📍 로그인 페이지 접속 중...")
    page.goto('https://perso.ai/ko/login', timeout=30000)
    page.wait_for_load_state('networkidle')
    
    await log("📝 이메일 입력 중...")
    email_input = page.locator('input[type="email"], input[placeholder*="이메일"]')
    email_input.fill(email)
    time.sleep(0.5)
    
    await log("👆 계속 버튼 클릭...")
    continue_button = page.locator('button:has-text("계속")')
    continue_button.click()
    time.sleep(2)
    
    await log("🔐 비밀번호 입력 중...")
    password_input = page.locator('input[type="password"]')
    password_input.fill(password)
    time.sleep(0.5)
    
    await log("🚪 Enter 키로 로그인 제출...")
    password_input.press('Enter')
    
    await log("⏳ 로그인 처리 중...")
    page.wait_for_url('**/workspace/**', timeout=15000)
    
    await log("✅ 로그인 성공!")
    time.sleep(2)
