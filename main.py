import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
import database as db
from middlewares import UserAndSubMiddleware

from handlers import (
    start,
    user,
    admin_main,
    admin_anime,
    admin_episode,
    admin_channel,
    admin_user,
    admin_settings
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dummy health-check server (Render port binding requirement)
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    logger.info("Initializing Database...")
    await db.init_db()

    # 1. Start dummy HTTP server for Web Service port binding (Render/Koyeb/etc.)
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Dummy HTTP server started on port {port}")

    # 2. Telegram bot polling
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Register Middlewares
    middleware = UserAndSubMiddleware()
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)

    # Register Routers
    dp.include_router(start.router)
    dp.include_router(admin_main.router)
    dp.include_router(admin_anime.router)
    dp.include_router(admin_episode.router)
    dp.include_router(admin_channel.router)
    dp.include_router(admin_user.router)
    dp.include_router(admin_settings.router)
    dp.include_router(user.router)

    logger.info("Bot started polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
