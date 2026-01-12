import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pathlib import Path
import sys

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tasks.test_login import test_login_sync
from tasks.test_upload import test_upload_sync

logger = logging.getLogger("perso-auto-tester")
router = APIRouter()

@router.websocket("/ws/{test_type}")
async def websocket_test(websocket: WebSocket, test_type: str):
    """WebSocket으로 테스트 실행 및 로그 스트리밍"""
    await websocket.accept()
    logger.info(f"WebSocket connected: {test_type}")
    
    try:
        # 로그 전송 함수
        async def send_log(msg: str):
            try:
                await websocket.send_json({"type": "log", "message": msg})
            except:
                pass
        
        # 별도 스레드에서 동기 함수 실행
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        
        if test_type == "login":
            await websocket.send_json({"type": "log", "message": "🚀 로그인 테스트 시작..."})
            
            result = await loop.run_in_executor(
                executor,
                test_login_sync,
                send_log
            )
            
            # 결과 전송
            await websocket.send_json({
                "type": "result",
                "success": result["success"],
                "message": result["message"],
                "screenshot": result.get("screenshot")
            })
            
        elif test_type == "upload":
            await websocket.send_json({"type": "log", "message": "🚀 업로드 테스트 시작..."})
            
            result = await loop.run_in_executor(
                executor,
                test_upload_sync,
                send_log
            )
            
            # 결과 전송
            await websocket.send_json({
                "type": "result",
                "success": result["success"],
                "message": result["message"],
                "screenshot": result.get("screenshot")
            })
            
        else:
            await websocket.send_json({
                "type": "result",
                "success": False,
                "message": "지원하지 않는 테스트 타입입니다"
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "result",
                "success": False,
                "message": f"테스트 실행 중 에러: {str(e)}"
            })
        except:
            pass