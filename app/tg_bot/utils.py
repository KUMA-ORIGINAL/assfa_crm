import logging
import httpx

from django.conf import settings

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"


def send_telegram_message(chat_id: str, message: str, button_text: str = None, button_url: str = None):
    if not chat_id:
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text=button_text, url=button_url),
        ]
    ])

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        'reply_markup': keyboard.to_dict(),
    }

    try:
        response = httpx.post(TELEGRAM_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"Message with order actions sent successfully to chat ID {chat_id}")
        else:
            logger.error(f"Failed to send order actions to {chat_id}: {response.text}")
    except Exception as e:
        logger.exception(f"An error occurred when sending order actions to {chat_id}: {str(e)}")
