import os
from dotenv import load_dotenv
from telegram import Bot
import logging
import datetime as dt

load_dotenv()

def get_telegram_config():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in the .env file")
    
    return bot_token, chat_id

def send_telegram_message(message):
    try:
        bot_token, chat_id = get_telegram_config()
        bot = Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message)
        logging.info("[+] Telegram message sent successfully")
        return True
    except ValueError as e:
        logging.error(f"[{dt.datetime.now()}] {e}")
        return False
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Error sending Telegram message: {e}")
        return False