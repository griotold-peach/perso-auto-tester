import asyncio

def create_logger(log_callback=None):
    """테스트용 로거 생성
    
    Args:
        log_callback: WebSocket 등으로 로그 전송할 콜백 함수
        
    Returns:
        log 함수
    """
    def log(msg):
        """콘솔 출력 + 콜백 전송"""
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
    
    return log