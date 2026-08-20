from aiogram import Router, F
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from middlewares import check_user_subscriptions
from keyboards.user_kb import get_main_keyboard, get_sub_keyboard, get_anime_detail_keyboard
from utils.helpers import parse_start_payload, format_anime_text

router = Router()

async def process_deep_link(event: Message | CallbackQuery, payload: str, bot, is_adm: bool):
    code, ep_num = parse_start_payload(payload)
    if not code:
        start_text = await db.get_setting("start_text", "🎬 Anime botga xush kelibsiz!")
        kb = get_main_keyboard(is_adm)
        if isinstance(event, Message):
            await event.answer(start_text, reply_markup=kb)
        else:
            await event.message.answer(start_text, reply_markup=kb)
        return

    anime = await db.get_anime_by_code(code)
    if not anime:
        msg_text = f"❌ **{code}** kodli anime topilmadi!"
        if isinstance(event, Message):
            await event.answer(msg_text)
        else:
            await event.message.answer(msg_text)
        return

    # If episode number is specified (deep link format: start=125_04)
    if ep_num is not None:
        episode = await db.get_episode(code, ep_num)
        if episode:
            caption = f"🎬 **{anime['title']}**\n📺 **{ep_num}-qism**"
            if isinstance(event, Message):
                await event.answer_video(video=episode['video_file_id'], caption=caption)
            else:
                await event.message.answer_video(video=episode['video_file_id'], caption=caption)
            await db.increment_user_episodes(event.from_user.id)
            return
        else:
            msg_text = f"🎬 **{anime['title']}**\n❌ {ep_num}-qism hali yuklanmagan!"
            if isinstance(event, Message):
                await event.answer(msg_text)
            else:
                await event.message.answer(msg_text)
            return

    # If only anime code is specified (deep link format: start=125)
    text = format_anime_text(anime)
    kb = get_anime_detail_keyboard(code)
    if anime['poster_file_id']:
        try:
            if isinstance(event, Message):
                await event.answer_photo(photo=anime['poster_file_id'], caption=text, reply_markup=kb)
            else:
                await event.message.answer_photo(photo=anime['poster_file_id'], caption=text, reply_markup=kb)
            return
        except Exception:
            pass

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.answer(text, reply_markup=kb)

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, bot, state: FSMContext, is_admin: bool = False):
    await state.clear()
    payload = command.args or ""
    
    # Check mandatory channels subscription
    is_subbed = await check_user_subscriptions(bot, message.from_user.id)
    if not is_subbed and not is_admin:
        channels = await db.get_channels()
        sub_text = await db.get_setting("sub_text", "Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:")
        kb = get_sub_keyboard(channels, payload=payload)
        await message.answer(f"👋 Assalomu alaykum!\n\n{sub_text}", reply_markup=kb)
        return

    # User is subscribed or admin
    if payload:
        await process_deep_link(message, payload, bot, is_admin)
    else:
        start_text = await db.get_setting("start_text", "👋 Assalomu alaykum!\n\n🎬 Anime botga xush kelibsiz!")
        kb = get_main_keyboard(is_admin)
        await message.answer(start_text, reply_markup=kb)

@router.callback_query(F.data.startswith("check_sub"))
async def callback_check_sub(call: CallbackQuery, bot, is_admin: bool = False):
    payload = ""
    if ":" in call.data:
        payload = call.data.split(":", 1)[1]
        
    is_subbed = await check_user_subscriptions(bot, call.from_user.id)
    if not is_subbed and not is_admin:
        await call.answer(
            "❌ Siz hali barcha kanallarga obuna bo‘lmagansiz!\n\nIltimos, kanallarga obuna bo‘ling va qaytadan tekshiring.",
            show_alert=True
        )
        return

    await call.answer("✅ Obuna tasdiqlandi!")
    try:
        await call.message.delete()
    except Exception:
        pass

    if payload:
        await process_deep_link(call, payload, bot, is_admin)
    else:
        start_text = await db.get_setting("start_text", "🎬 Anime botga xush kelibsiz!")
        kb = get_main_keyboard(is_admin)
        await call.message.answer(f"✅ Obuna tasdiqlandi!\n\n{start_text}", reply_markup=kb)
