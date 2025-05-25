import telegram
from dotenv import load_dotenv
import os

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    def send_alert(self, video_id: str):
        self.bot.send_message(
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            text=f"🎥 New Short Uploaded!\nhttps://youtu.be/{video_id}"
        )