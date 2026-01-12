from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    """메인 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PERSO Auto Tester</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .button-group {
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                cursor: pointer;
                font-size: 16px;
                border-radius: 10px;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
                flex: 1;
                min-width: 200px;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
            }
            .status {
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: none;
            }
            .status.active {
                display: block;
            }
            .status.loading {
                background: #e3f2fd;
                color: #1976d2;
                border-left: 4px solid #2196F3;
            }
            .status.success {
                background: #e8f5e9;
                color: #2e7d32;
                border-left: 4px solid #4caf50;
            }
            .status.error {
                background: #ffebee;
                color: #c62828;
                border-left: 4px solid #f44336;
            }
            .logs {
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.6;
                max-height: 400px;
                overflow-y: auto;
                margin-bottom: 20px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .logs:empty {
                display: none;
            }
            .screenshot {
                margin-top: 20px;
                text-align: center;
            }
            .screenshot img {
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .screenshot-title {
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 PERSO Auto Tester</h1>
            <p class="subtitle">PERSO.AI 자동화 테스트 시스템</p>
            
            <div class="button-group">
                <button onclick="runTest('login')" id="loginBtn">
                    🔐 로그인 테스트
                </button>
                <button onclick="runTest('upload')" id="uploadBtn" disabled>
                    📤 업로드 + 번역 테스트 (준비중)
                </button>
            </div>
            
            <div id="status" class="status"></div>
            
            <div id="logs" class="logs"></div>
            
            <div id="screenshot" class="screenshot"></div>
        </div>
        
        <script>
            let ws = null;
            
            function runTest(testType) {
                const statusDiv = document.getElementById('status');
                const logsDiv = document.getElementById('logs');
                const screenshotDiv = document.getElementById('screenshot');
                const loginBtn = document.getElementById('loginBtn');
                
                // 초기화
                logsDiv.textContent = '';
                screenshotDiv.innerHTML = '';
                statusDiv.className = 'status active loading';
                statusDiv.innerHTML = '<span class="spinner"></span>테스트 실행 중...';
                loginBtn.disabled = true;
                
                // WebSocket 연결
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/test/ws/${testType}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {
                    console.log('WebSocket 연결됨');
                };
                
                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'log') {
                            logsDiv.textContent += data.message + '\\n';
                            logsDiv.scrollTop = logsDiv.scrollHeight;
                        } else if (data.type === 'result') {
                            if (data.success) {
                                statusDiv.className = 'status active success';
                                statusDiv.textContent = '✅ ' + data.message;
                                
                                if (data.screenshot) {
                                    screenshotDiv.innerHTML = `
                                        <div class="screenshot-title">📸 테스트 결과 스크린샷</div>
                                        <img src="/screenshots/${data.screenshot}" alt="Test Result" />
                                    `;
                                }
                            } else {
                                statusDiv.className = 'status active error';
                                statusDiv.textContent = '❌ ' + data.message;
                                
                                if (data.screenshot) {
                                    screenshotDiv.innerHTML = `
                                        <div class="screenshot-title">📸 에러 스크린샷</div>
                                        <img src="/screenshots/${data.screenshot}" alt="Error" />
                                    `;
                                }
                            }
                            
                            loginBtn.disabled = false;
                            ws.close();
                        }
                    } catch (e) {
                        console.error('메시지 파싱 에러:', e);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket 에러:', error);
                    statusDiv.className = 'status active error';
                    statusDiv.textContent = '❌ 연결 오류가 발생했습니다';
                    loginBtn.disabled = false;
                };
                
                ws.onclose = () => {
                    console.log('WebSocket 연결 종료');
                    loginBtn.disabled = false;
                };
            }
        </script>
    </body>
    </html>
    """
    return html_content
