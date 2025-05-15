import httpx
from django.conf import settings


TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"


def send_telegram_message(chat_id: str, message: str):
    if not chat_id:
        return

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        httpx.post(TELEGRAM_API_URL, data=payload, timeout=5)
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")
