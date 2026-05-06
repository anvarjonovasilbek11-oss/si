"""
Telegram Bot with aiogram
Handles bot updates and WebApp launch
"""
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from db import SessionLocal
from models import User
from gemini_client import get_welcome_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def get_webapp_keyboard() -> InlineKeyboardMarkup:
    """
    MODULE 4: Create keyboard with WebApp button
    Button text: "Open HR Assistant 🌐"
    Opens Telegram WebApp URL
    
    Returns:
        InlineKeyboardMarkup with WebApp button
    """
    webapp_url = f"{Config.WEBAPP_URL}/webapp"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Open HR Assistant 🌐",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )
    
    return keyboard


def save_or_update_user(telegram_user: types.User) -> User:
    """
    Save or update user in database
    
    Args:
        telegram_user: Telegram user object
        
    Returns:
        User model instance
    """
    db = SessionLocal()
    
    try:
        # Check if user exists
        user = db.query(User).filter(
            User.telegram_id == telegram_user.id
        ).first()
        
        if user:
            # Update existing user
            user.username = telegram_user.username
            user.first_name = telegram_user.first_name
            user.last_name = telegram_user.last_name
            user.language_code = telegram_user.language_code or "en"
        else:
            # Create new user
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code or "en"
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    finally:
        db.close()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Handle /start command
    Shows welcome message - direct messaging enabled
    """
    # Save user to database
    save_or_update_user(message.from_user)
    
    # Get user's language
    lang = message.from_user.language_code or "en"
    if lang not in Config.SUPPORTED_LANGUAGES:
        lang = "en"
    
    # Get welcome message
    welcome_text = get_welcome_message(lang)
    
    # Additional instructions for direct messaging
    instructions = {
        "uz": "\n\n💬 Menga HR bo'yicha har qanday savol bering!\n\nMisol:\n• Necha kun ta'til?\n• Ish haqi qanday?\n• Kompaniya qoidalari",
        "ru": "\n\n💬 Задайте мне любой вопрос по HR!\n\nПримеры:\n• Сколько дней отпуска?\n• Как насчет зарплаты?\n• Правила компании",
        "en": "\n\n💬 Ask me any HR question!\n\nExamples:\n• How many vacation days?\n• What about salary?\n• Company policies"
    }
    
    full_message = welcome_text + instructions.get(lang, instructions["en"])
    
    # Send message without WebApp button (direct messaging works!)
    await message.answer(full_message)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Handle /help command
    Shows help information
    """
    lang = message.from_user.language_code or "en"
    if lang not in Config.SUPPORTED_LANGUAGES:
        lang = "en"
    
    help_texts = {
        "uz": (
            "🤖 HR Yordamchisi\n\n"
            "Men sizga HR savollariga javob berishda yordam beraman:\n"
            "• Ta'til siyosati\n"
            "• Ish haqi\n"
            "• Kompaniya qoidalari\n"
            "• Imtiyozlar\n"
            "• Va boshqalar\n\n"
            "/start - Botni ishga tushirish\n"
            "/help - Yordam"
        ),
        "ru": (
            "🤖 HR-Ассистент\n\n"
            "Я помогу вам ответить на вопросы по HR:\n"
            "• Политика отпусков\n"
            "• Заработная плата\n"
            "• Правила компании\n"
            "• Льготы\n"
            "• И многое другое\n\n"
            "/start - Запустить бота\n"
            "/help - Помощь"
        ),
        "en": (
            "🤖 HR Assistant\n\n"
            "I can help you with HR-related questions:\n"
            "• Vacation policy\n"
            "• Payroll\n"
            "• Company policies\n"
            "• Benefits\n"
            "• And more\n\n"
            "/start - Start the bot\n"
            "/help - Help"
        )
    }
    
    await message.answer(
        help_texts.get(lang, help_texts["en"])
    )


@dp.message()
async def handle_message(message: types.Message):
    """
    Handle regular messages
    Sends user message to hrbot_gemini API and returns response
    """
    import requests
    
    # Get user's message
    user_message = message.text
    
    if not user_message:
        return
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Send to hrbot_gemini API
        api_url = "http://localhost:8000/chat"
        response = requests.post(
            api_url,
            json={"message": user_message},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("reply", "No response received.")
            
            # Send answer back to user
            await message.answer(answer)
        else:
            # API error
            await message.answer(
                "⚠️ Sorry, the HR assistant is temporarily unavailable. Please try again later."
            )
    
    except requests.exceptions.ConnectionError:
        # API not reachable
        await message.answer(
            "⚠️ Sorry, the HR assistant is temporarily unavailable. Please try again later."
        )
    
    except requests.exceptions.Timeout:
        # Request timeout
        await message.answer(
            "⚠️ The request took too long. Please try again with a shorter question."
        )
    
    except Exception as e:
        logger.error(f"Error calling hrbot_gemini API: {e}")
        await message.answer(
            "⚠️ Sorry, the HR assistant is temporarily unavailable. Please try again later."
        )


async def start_bot():
    """Start the bot"""
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


async def stop_bot():
    """Stop the bot"""
    logger.info("Stopping Telegram bot...")
    await bot.session.close()


if __name__ == "__main__":
    import asyncio
    
    print("Starting HR Assistant Telegram Bot...")
    print(f"Bot token configured: {bool(Config.TELEGRAM_BOT_TOKEN)}")
    
    asyncio.run(start_bot())
