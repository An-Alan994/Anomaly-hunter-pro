import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_PATH = os.getenv("DB_PATH", "anomaly.db")

    KUCOIN_KEY = os.getenv("KUCOIN_KEY")
    KUCOIN_SECRET = os.getenv("KUCOIN_SECRET")
    KUCOIN_PASSPHRASE = os.getenv("KUCOIN_PASSPHRASE")

    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.02"))
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.1"))

    TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "False").lower() == "true"
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
