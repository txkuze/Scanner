import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')

    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_NAME = os.getenv('MONGODB_NAME', 'telegram_bot')

    OWNER_ID = int(os.getenv('OWNER_ID', 0))
    LOG_GROUP_ID = int(os.getenv('LOG_GROUP_ID', -1003228624224))

    MAX_CONCURRENT_SCANS = int(os.getenv('MAX_CONCURRENT_SCANS', 3))
    SCAN_TIMEOUT = int(os.getenv('SCAN_TIMEOUT', 300))
    REPORT_DIR = os.getenv('REPORT_DIR', 'reports')

    CHAT_TRIGGERS = ['hi', 'hello', 'hey', 'sup', 'yo', 'greetings', 'good morning', 'good evening', 'good afternoon']

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in .env file")
        if not cls.API_ID:
            raise ValueError("API_ID is required in .env file")
        if not cls.API_HASH:
            raise ValueError("API_HASH is required in .env file")
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is required in .env file")
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI is required in .env file")
        if not cls.OWNER_ID:
            raise ValueError("OWNER_ID is required in .env file")

        os.makedirs(cls.REPORT_DIR, exist_ok=True)
