"""
Configuration module for HR Telegram WebApp Bot
Loads environment variables and provides app configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/hr_telegram_bot"
    )
    
    # FastAPI
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    WEBAPP_URL = os.getenv("WEBAPP_URL", f"http://localhost:{API_PORT}")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # Supported languages
    SUPPORTED_LANGUAGES = ["uz", "ru", "en"]
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        return True


# Validate configuration on import
Config.validate()
