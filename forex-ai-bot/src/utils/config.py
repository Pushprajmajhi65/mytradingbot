from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TWELVEDATA_KEY = os.getenv("TWELVEDATA_API_KEY")

    # Trading Parameters
    SYMBOLS = ["EUR/USD", "USD/JPY"]
    RISK_PER_TRADE = 0.02
    POLLING_INTERVAL = 300  # 5 minutes