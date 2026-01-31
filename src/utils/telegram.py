import os
import logging
import datetime as dt

import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

def get_telegram_config():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in the .env file")
    
    return bot_token, chat_id

def send_telegram_message(message):
    try:
        bot_token, chat_id = get_telegram_config()
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        prefix = f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TakeOver Alert:\n"
        payload = {"chat_id": chat_id, "text": prefix + message}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("Telegram message sent successfully")
        return True
    except ValueError as e:
        logging.error(f"{e}")
        return False
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")
        return False