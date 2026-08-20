import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
import database as db
from keyboards.user_kb import get_sub_keyboard

logger = logging.getLogger(__name__)

def normalize_channel_id(ch_input: str) -> str:
    ch_input = ch_input.strip()
    if "t.me/" in ch_input:
        username = ch_input.split("t.me/")[-1].strip("/").strip()
        if not username.startswith("@") and not username.startswith("-"):
            return f"@{username}"
        return username
    if not ch_input.startswith("@") and not ch_input.startswith("-"):
        return f"@{ch_input}"
    return ch_input

async def check_user_subscriptions(bot, user_id: int) -> bool:
    channels = await db.get_channels()
    if not channels:
        return True
    
    for ch in channels:
        ch_id = normalize_channel_id(ch['channel_id'])
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status not in ["creator", "administrator", "member"]:
                return False
        except Exception as e:
            logger.warning(f"Could not check chat member for channel {ch_id} and user {user_id}: {e}")
            # If get_chat_member raises an exception (e.g. user not found in channel), user is NOT subscribed
            return False
    return True

class UserAndSubMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot = data["bot"]
        user = None
        
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            
        if user:
            # Register or update user activity
            await db.add_or_update_user(
                user_id=user.id,
                full_name=user.full_name or "",
                username=user.username or ""
            )
            
            # Check if user is blocked
            db_user = await db.get_user(user.id)
            if db_user and db_user['is_blocked']:
                if isinstance(event, Message):
                    await event.answer("❌ Siz botdan bloklangansiz!")
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Siz botdan bloklangansiz!", show_alert=True)
                return
            
            # Check admin status
            is_adm = await db.is_admin(user.id)
            data["is_admin"] = is_adm
            
            # Mandatory subscription check bypass for admin or /start command or check_sub callback
            is_start_cmd = False
            if isinstance(event, Message) and event.text and event.text.startswith("/start"):
                is_start_cmd = True
            
            is_check_sub_cb = False
            if isinstance(event, CallbackQuery) and event.data and event.data.startswith("check_sub"):
                is_check_sub_cb = True
                
            if not is_adm and not is_start_cmd and not is_check_sub_cb:
                is_subbed = await check_user_subscriptions(bot, user.id)
                if not is_subbed:
                    channels = await db.get_channels()
                    sub_text = await db.get_setting("sub_text", "Botdan foydalanish uchun kanallarga obuna bo'ling:")
                    kb = get_sub_keyboard(channels)
                    
                    if isinstance(event, Message):
                        await event.answer(f"{sub_text}", reply_markup=kb)
                    elif isinstance(event, CallbackQuery):
                        await event.answer("❌ Siz hali barcha kanallarga obuna bo‘lmagansiz!", show_alert=True)
                        try:
                            await event.message.answer(f"{sub_text}", reply_markup=kb)
                        except Exception:
                            pass
                    return

        return await handler(event, data)
