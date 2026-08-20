import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID", "123456789"))
DB_PATH = os.getenv("DB_PATH", "anime_bot.db")

DEFAULT_START_TEXT = """👋 Assalomu alaykum!

🎬 Anime botga xush kelibsiz!
Quyidagi bo'limlardan birini tanlang:"""

DEFAULT_SUB_TEXT = """👋 Assalomu alaykum!

Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:"""
