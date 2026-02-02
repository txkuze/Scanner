import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    OWNER_ID = int(os.getenv('OWNER_ID', 0))
    LOG_GROUP_ID = int(os.getenv('LOG_GROUP_ID', -1003228624224))

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
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required in .env file")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required in .env file")
        if not cls.OWNER_ID:
            raise ValueError("OWNER_ID is required in .env file")

        os.makedirs(cls.REPORT_DIR, exist_ok=True)
