import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')

    MAX_CONCURRENT_SCANS = int(os.getenv('MAX_CONCURRENT_SCANS', 3))
    SCAN_TIMEOUT = int(os.getenv('SCAN_TIMEOUT', 300))
    REPORT_DIR = os.getenv('REPORT_DIR', 'reports')

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in .env file")
        if not cls.API_ID:
            raise ValueError("API_ID is required in .env file")
        if not cls.API_HASH:
            raise ValueError("API_HASH is required in .env file")

        os.makedirs(cls.REPORT_DIR, exist_ok=True)
