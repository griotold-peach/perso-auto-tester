from .login import login
from .popup_handler import accept_cookies, close_hubspot_iframe_popup, close_all_popups
from .config import (
    PERSO_EMAIL,
    PERSO_PASSWORD,
    PERSO_URL,
    VIDEO_FILE_PATH,
    HEADLESS,
    SCREENSHOT_DIR
)

__all__ = [
    'login',
    'accept_cookies',
    'close_hubspot_iframe_popup',
    'close_all_popups',
    'PERSO_EMAIL',
    'PERSO_PASSWORD',
    'PERSO_URL',
    'VIDEO_FILE_PATH',
    'HEADLESS',
    'SCREENSHOT_DIR',
]
