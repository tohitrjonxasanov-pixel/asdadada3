import math
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from states.states import UserStates
from middlewares import check_user_subscriptions
from keyboards.user_kb import (
    get_main_keyboard,
    get_sub_keyboard,
    get_anime_detail_keyboard,
    get_episodes_grid_keyboard,
    get_catalog_keyboard
)
from utils.helpers import format_anime_text

router = Router()

# --- BACK TO MAIN MENU (Reply Keyboard Orqaga or Callback) ---
@router.message(F.text == "⬅️ Orqaga")
async def msg_global_back_main(message: Message, state: FSMContext, is_admin: bool = False):
    await state.clear()
    kb = get_main_keyboard(is_admin)
    start_text = await db.get_setting("start_text", "🎬 Anime botga xush kelibsiz!")
    await message.answer(start_text, reply_markup=kb)

@router.callback_query(F.data == "user_back_main")
async def callback_back_main(call: CallbackQuery, state: FSMContext, is_admin: bool = False):
    await state.clear()
    await call.answer()
    try:
        await call.message.delete()
    except Exception:
        pass
    kb = get_main_keyboard(is_admin)
    start_text = await db.get_setting("start_text", "🎬 Anime botga xush kelibsiz!")
    await call.message.answer(start_text, reply_markup=kb)

# --- SEARCH BY NAME ---
@router.message(F.text == "🔎 Anime qidirish")
async def cmd_search_title(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_search_title)
    await message.answer("🔎 Anime nomini yuboring:")

@router.message(UserStates.waiting_for_search_title)
async def process_search_title(message: Message, state: FSMContext):
    query = message.text.strip()
    if query == "⬅️ Orqaga":
        await msg_global_back_main(message, state)
        return

    results = await db.search_anime_by_title(query)
    await state.clear()

    if not results:
        await message.answer("❌ Bu nom bo'yicha hech qanday anime topilmadi. Qaytadan urinib ko'ring.")
        return

    if len(results) == 1:
        anime = results[0]
        text = format_anime_text(anime)
        kb = get_anime_detail_keyboard(anime['code'])
        if anime['poster_file_id']:
            try:
                await message.answer_photo(photo=anime['poster_file_id'], caption=text, reply_markup=kb)
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=kb)
    else:
        builder = InlineKeyboardBuilder()
        for a in results:
            builder.button(text=f"🎬 {a['title']}", callback_data=f"view_anime:{a['code']}")
        builder.adjust(1)
        builder.button(text="⬅️ Orqaga", callback_data="user_back_main")
        await message.answer(f"🔎 **\"{query}\"** bo'yicha topilgan animelar:", reply_markup=builder.as_markup())

# --- SEARCH BY CODE ---
@router.message(F.text == "🔢 Kod orqali qidirish")
async def cmd_search_code(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_search_code)
    await message.answer("🔢 Anime kodini yuboring:")

@router.message(UserStates.waiting_for_search_code)
async def process_search_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if code == "⬅️ Orqaga":
        await msg_global_back_main(message, state)
        return

    await state.clear()
    anime = await db.get_anime_by_code(code)

    if not anime:
        await message.answer(f"❌ **{code}** kodli anime topilmadi!")
        return

    text = format_anime_text(anime)
    episodes = await db.get_episodes_by_anime(code)
    kb = get_episodes_grid_keyboard(code, episodes)

    if anime['poster_file_id']:
        try:
            await message.answer_photo(photo=anime['poster_file_id'], caption=text, reply_markup=kb)
            return
        except Exception:
            pass
    await message.answer(text, reply_markup=kb)

# --- CATALOG ---
@router.message(F.text == "📚 Anime katalogi")
async def cmd_catalog(message: Message, state: FSMContext):
    await state.clear()
    await send_catalog_page(message, page=0)

async def send_catalog_page(message_or_call, page: int):
    items_per_page = 5
    total_animes = await db.get_animes_count()
    if total_animes == 0:
        text = "📚 **ANIME KATALOGI**\n\nHozircha animelar mavjud emas."
        if isinstance(message_or_call, Message):
            await message_or_call.answer(text)
        else:
            await message_or_call.message.answer(text)
        return

    total_pages = math.ceil(total_animes / items_per_page)
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    animes = await db.get_all_animes(limit=items_per_page, offset=page * items_per_page)
    text = "🎬 **ANIME KATALOGI**\n\nKerakli animeni tanlang:"
    kb = get_catalog_keyboard(animes, page, total_pages)

    if isinstance(message_or_call, Message):
        await message_or_call.answer(text, reply_markup=kb)
    else:
        try:
            await message_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await message_or_call.message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("catalog_page:"))
async def callback_catalog_page(call: CallbackQuery):
    await call.answer()
    page = int(call.data.split(":")[1])
    await send_catalog_page(call, page)

# --- VIEW ANIME DETAILS ---
@router.callback_query(F.data.startswith("view_anime:"))
async def callback_view_anime(call: CallbackQuery):
    await call.answer()
    code = call.data.split(":")[1]
    anime = await db.get_anime_by_code(code)
    if not anime:
        await call.answer("❌ Anime topilmadi!", show_alert=True)
        return

    text = format_anime_text(anime)
    kb = get_anime_detail_keyboard(code)

    try:
        await call.message.delete()
    except Exception:
        pass

    if anime['poster_file_id']:
        try:
            await call.message.answer_photo(photo=anime['poster_file_id'], caption=text, reply_markup=kb)
            return
        except Exception:
            pass

    await call.message.answer(text, reply_markup=kb)

# --- VIEW EPISODES GRID ---
@router.callback_query(F.data.startswith("view_eps:"))
async def callback_view_episodes(call: CallbackQuery):
    code = call.data.split(":")[1]
    anime = await db.get_anime_by_code(code)
    if not anime:
        await call.answer("❌ Anime topilmadi!", show_alert=True)
        return

    episodes = await db.get_episodes_by_anime(code)
    if not episodes:
        await call.answer("❌ Bu animega hali qismlar yuklanmagan!", show_alert=True)
        return

    await call.answer()
    text = f"🎬 **{anime['title']}**\n📺 Qismlarni tanlang:"
    kb = get_episodes_grid_keyboard(code, episodes)

    try:
        await call.message.edit_caption(caption=text, reply_markup=kb)
    except Exception:
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await call.message.answer(text, reply_markup=kb)

# --- GET EPISODE VIDEO ---
@router.callback_query(F.data.startswith("get_ep:"))
async def callback_get_episode(call: CallbackQuery, bot, is_admin: bool = False):
    parts = call.data.split(":")
    code = parts[1]
    ep_num = int(parts[2])

    # Mandatory channel subscription check before delivering video
    is_subbed = await check_user_subscriptions(bot, call.from_user.id)
    if not is_subbed and not is_admin:
        channels = await db.get_channels()
        sub_text = await db.get_setting("sub_text", "Botdan foydalanish uchun kanallarga obuna bo'ling:")
        kb = get_sub_keyboard(channels, payload=f"{code}_{ep_num:02d}")
        await call.answer("❌ Video olish uchun barcha kanallarga obuna bo'ling!", show_alert=True)
        await call.message.answer(sub_text, reply_markup=kb)
        return

    anime = await db.get_anime_by_code(code)
    episode = await db.get_episode(code, ep_num)

    if not episode:
        await call.answer("❌ Bu qism topilmadi!", show_alert=True)
        return

    await call.answer()
    title = anime['title'] if anime else f"Anime #{code}"
    caption = f"🎬 **{title}**\n📺 **{ep_num}-qism**"
    
    await call.message.answer_video(video=episode['video_file_id'], caption=caption)
    await db.increment_user_episodes(call.from_user.id)
