import math
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from states.states import AdminAnimeAdd, AdminAnimeEdit
from keyboards.admin_kb import (
    get_admin_anime_menu,
    get_admin_main_keyboard,
    get_admin_anime_detail_keyboard,
    get_admin_anime_edit_fields_keyboard,
    get_confirm_keyboard,
    get_delete_confirm_keyboard
)
from utils.helpers import get_bot_username, generate_anime_link, format_anime_admin_text

router = Router()

@router.message(F.text == "🎬 Anime boshqarish")
async def msg_admin_anime_menu(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.clear()
    kb = get_admin_anime_menu()
    await message.answer("🎬 **ANIME BOSHQARISH**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "⬅️ Orqaga")
async def msg_admin_back(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

# --- ADD ANIME WIZARD ---
@router.message(F.text == "➕ Anime qo‘shish")
async def cmd_add_anime_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.set_state(AdminAnimeAdd.title)
    await message.answer("🎬 Anime nomini yuboring:")

@router.message(AdminAnimeAdd.title)
async def process_add_anime_title(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAnimeAdd.poster)
    await message.answer("🖼 Anime posterini yuboring:\n(Rasm yuboring yoki o'tkazib yuborish uchun text yozing)")

@router.message(AdminAnimeAdd.poster)
async def process_add_anime_poster(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return
    poster_id = ""
    if message.photo:
        poster_id = message.photo[-1].file_id
    await state.update_data(poster=poster_id)
    await state.set_state(AdminAnimeAdd.genre)
    await message.answer("🎭 Janrini yuboring:\n(Masalan: Action, Fantasy, Adventure)")

@router.message(AdminAnimeAdd.genre)
async def process_add_anime_genre(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return
    await state.update_data(genre=message.text.strip())
    await state.set_state(AdminAnimeAdd.year)
    await message.answer("📅 Chiqqan yilini yuboring:\n(Masalan: 2024)")

@router.message(AdminAnimeAdd.year)
async def process_add_anime_year(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return
    try:
        year = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Iltimos, yilni raqamlarda yuboring (masalan: 2024):")
        return
    await state.update_data(year=year)
    await state.set_state(AdminAnimeAdd.total_episodes)
    await message.answer("📺 Umumiy qism sonini yuboring:\n(Masalan: 25)")

@router.message(AdminAnimeAdd.total_episodes)
async def process_add_anime_total_episodes(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return
    try:
        total = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Iltimos, qism sonini raqamlarda yuboring (masalan: 25):")
        return
    await state.update_data(total_episodes=total)
    await state.set_state(AdminAnimeAdd.description)
    await message.answer("📝 Anime tavsifini yuboring:")

@router.message(AdminAnimeAdd.description)
async def process_add_anime_description(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return
    await state.update_data(description=message.text.strip())
    data = await state.get_data()
    
    text = (
        f"🎬 **{data['title']}**\n\n"
        f"🎭 {data['genre']}\n"
        f"📅 {data['year']}\n"
        f"📺 {data['total_episodes']} qism\n\n"
        f"📝 {data['description']}\n\n"
        f"Hammasi to‘g‘rimi?"
    )
    kb = get_confirm_keyboard("adm_add_anime_confirm")
    await state.set_state(AdminAnimeAdd.confirm)
    
    if data['poster']:
        try:
            await message.answer_photo(photo=data['poster'], caption=text, reply_markup=kb)
            return
        except Exception:
            pass
    await message.answer(text, reply_markup=kb)

@router.callback_query(AdminAnimeAdd.confirm, F.data.startswith("adm_add_anime_confirm_"))
async def process_add_anime_confirm(call: CallbackQuery, state: FSMContext, bot):
    action = call.data.split("_")[-1]
    if action == "no":
        await state.clear()
        await call.answer("❌ Anime qo'shish bekor qilindi.")
        try:
            await call.message.delete()
        except Exception:
            pass
        kb = get_admin_anime_menu()
        await call.message.answer("🎬 **ANIME BOSHQARISH**", reply_markup=kb)
        return

    data = await state.get_data()
    await state.clear()
    code = await db.get_next_anime_code()
    
    await db.add_anime(
        code=code,
        title=data['title'],
        poster_file_id=data['poster'],
        genre=data['genre'],
        year=data['year'],
        total_episodes=data['total_episodes'],
        description=data['description']
    )

    bot_username = await get_bot_username(bot)
    anime_link = generate_anime_link(bot_username, code)

    try:
        await call.message.delete()
    except Exception:
        pass

    success_msg = (
        f"✅ **Anime muvaffaqiyatli qo‘shildi!**\n\n"
        f"🔢 Kod: **{code}**\n\n"
        f"🔗 Anime linki:\n{anime_link}\n\n"
        f"Endi qismlarni qo‘shishingiz mumkin."
    )
    kb = get_admin_anime_menu()
    await call.message.answer(success_msg, reply_markup=kb)

# --- LIST ANIMES FOR ADMIN ---
@router.message(F.text == "📋 Anime ro‘yxati")
async def msg_admin_anime_list(message: Message, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await send_admin_anime_list_page(message, page=0)

async def send_admin_anime_list_page(message_or_call, page: int):
    items_per_page = 10
    total_animes = await db.get_animes_count()
    if total_animes == 0:
        text = "🎬 **ANIME RO‘YXATI**\n\nHozircha animelar yo'q."
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
    builder = InlineKeyboardBuilder()
    for a in animes:
        builder.button(text=f"[{a['code']}] {a['title']}", callback_data=f"adm_view_anime:{a['code']}")
    builder.adjust(1)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardBuilder().button(text="⬅️ Oldingi", callback_data=f"adm_anime_list:{page - 1}").buttons[0])
    if page < total_pages - 1:
        nav.append(InlineKeyboardBuilder().button(text="Keyingi ➡️", callback_data=f"adm_anime_list:{page + 1}").buttons[0])
    if nav:
        builder.row(*nav)

    text = f"🎬 **ANIME RO‘YXATI** ({total_animes} ta)\n\nKerakli animeni tanlang:"
    if isinstance(message_or_call, Message):
        await message_or_call.answer(text, reply_markup=builder.as_markup())
    else:
        try:
            await message_or_call.message.edit_text(text, reply_markup=builder.as_markup())
        except Exception:
            await message_or_call.message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("adm_anime_list:"))
async def callback_admin_anime_list(call: CallbackQuery):
    await call.answer()
    page = int(call.data.split(":")[1])
    await send_admin_anime_list_page(call, page)

# --- VIEW SINGLE ANIME IN ADMIN ---
@router.callback_query(F.data.startswith("adm_view_anime:"))
async def callback_admin_view_anime(call: CallbackQuery):
    await call.answer()
    code = call.data.split(":")[1]
    anime = await db.get_anime_by_code(code)
    if not anime:
        await call.answer("❌ Anime topilmadi!", show_alert=True)
        return

    episodes = await db.get_episodes_by_anime(code)
    uploaded_count = len(episodes)
    text = format_anime_admin_text(anime, uploaded_count)
    kb = get_admin_anime_detail_keyboard(code)

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

# --- SEARCH ANIME IN ADMIN ---
@router.message(F.text == "🔎 Anime qidirish")
async def msg_admin_search_anime(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.set_state(AdminAnimeEdit.waiting_for_anime_code)
    await message.answer("🔎 Qidirilayotgan anime nomini yoki kodini yuboring:")

@router.message(AdminAnimeEdit.waiting_for_anime_code)
async def process_admin_search_anime_input(message: Message, state: FSMContext, is_admin: bool = False):
    query = message.text.strip()
    if query == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return

    await state.clear()

    anime = await db.get_anime_by_code(query)
    if anime:
        episodes = await db.get_episodes_by_anime(query)
        text = format_anime_admin_text(anime, len(episodes))
        kb = get_admin_anime_detail_keyboard(query)
        if anime['poster_file_id']:
            try:
                await message.answer_photo(photo=anime['poster_file_id'], caption=text, reply_markup=kb)
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=kb)
        return

    results = await db.search_anime_by_title(query)
    if not results:
        await message.answer(f"❌ **\"{query}\"** bo'yicha anime topilmadi.")
        return

    builder = InlineKeyboardBuilder()
    for a in results:
        builder.button(text=f"[{a['code']}] {a['title']}", callback_data=f"adm_view_anime:{a['code']}")
    builder.adjust(1)
    await message.answer(f"🔎 Topilgan animelar:", reply_markup=builder.as_markup())

# --- EDIT ANIME ---
@router.message(F.text == "✏️ Anime tahrirlash")
async def msg_admin_edit_anime_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.set_state(AdminAnimeEdit.waiting_for_anime_code)
    await message.answer("✏️ Tahrirlamoqchi bo'lgan anime kodini yuboring:")

@router.callback_query(F.data.startswith("adm_edit_anime:"))
async def callback_admin_edit_anime(call: CallbackQuery):
    await call.answer()
    code = call.data.split(":")[1]
    anime = await db.get_anime_by_code(code)
    if not anime:
        await call.answer("❌ Anime topilmadi!", show_alert=True)
        return

    text = f"🎬 **{anime['title']}**\n\nNimani o‘zgartirmoqchisiz?"
    kb = get_admin_anime_edit_fields_keyboard(code)
    try:
        await call.message.edit_caption(caption=text, reply_markup=kb)
    except Exception:
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await call.message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("edit_field:"))
async def callback_select_field_to_edit(call: CallbackQuery, state: FSMContext):
    await call.answer()
    parts = call.data.split(":")
    code = parts[1]
    field = parts[2]

    await state.set_state(AdminAnimeEdit.waiting_for_new_value)
    await state.update_data(edit_code=code, edit_field=field)

    field_names = {
        "title": "yangi nomini",
        "poster_file_id": "yangi posterini (rasm qilib yuboring)",
        "genre": "yangi janrini",
        "year": "yangi chiqqan yilini",
        "total_episodes": "yangi umumiy qism sonini",
        "description": "yangi tavsifini"
    }

    prompt = f"Yangi {field_names.get(field, 'qiymatni')} yuboring:"
    await call.message.answer(prompt)

@router.message(AdminAnimeEdit.waiting_for_new_value)
async def process_admin_edit_new_value(message: Message, state: FSMContext, is_admin: bool = False):
    if message.text == "⬅️ Orqaga":
        await msg_admin_back(message, state, is_admin)
        return

    data = await state.get_data()
    code = data.get("edit_code")
    field = data.get("edit_field")
    await state.clear()

    if not code or not field:
        await message.answer("❌ Xatolik yuz berdi.")
        return

    val = message.text.strip() if message.text else ""
    if field == "poster_file_id" and message.photo:
        val = message.photo[-1].file_id
    elif field in ["year", "total_episodes"]:
        try:
            val = int(val)
        except ValueError:
            await message.answer("❌ Iltimos, son yuboring!")
            return

    await db.update_anime_field(code, field, val)
    anime = await db.get_anime_by_code(code)
    episodes = await db.get_episodes_by_anime(code)

    await message.answer(f"✅ Muvaffaqiyatli yangilandi!")
    text = format_anime_admin_text(anime, len(episodes))
    kb = get_admin_anime_detail_keyboard(code)
    await message.answer(text, reply_markup=kb)

# --- GET ANIME LINK IN ADMIN ---
@router.callback_query(F.data.startswith("adm_link_anime:"))
async def callback_admin_link_anime(call: CallbackQuery, bot):
    code = call.data.split(":")[1]
    anime = await db.get_anime_by_code(code)
    if not anime:
        await call.answer("❌ Anime topilmadi!", show_alert=True)
        return

    bot_username = await get_bot_username(bot)
    link = generate_anime_link(bot_username, code)
    await call.message.answer(f"🎬 **{anime['title']}**\n🔢 Kod: `{code}`\n\n🔗 Anime linki:\n`{link}`")
    await call.answer()

# --- DELETE ANIME ---
@router.message(F.text == "🗑 Anime o‘chirish")
async def msg_admin_delete_anime_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.set_state(AdminAnimeEdit.waiting_for_anime_code)
    await message.answer("🗑 O‘chirmoqchi bo'lgan anime kodini yuboring:")

@router.callback_query(F.data.startswith("adm_del_anime:"))
async def callback_admin_del_anime(call: CallbackQuery):
    code = call.data.split(":")[1]
    anime = await db.get_anime_by_code(code)
    if not anime:
        await call.answer("❌ Anime topilmadi!", show_alert=True)
        return

    text = (
        f"⚠️ **DIQQAT!**\n\n"
        f"**{anime['title']}**ni o‘chirmoqchimisiz?\n\n"
        f"Unga tegishli barcha qismlar ham o‘chiriladi!"
    )
    kb = get_delete_confirm_keyboard(f"confirm_del_anime:{code}")
    await call.message.answer(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("confirm_del_anime:"))
async def process_confirm_delete_anime(call: CallbackQuery):
    parts = call.data.split(":")
    code = parts[1]
    action = parts[2]

    if action == "no":
        await call.answer("O'chirish bekor qilindi.")
        try:
            await call.message.delete()
        except Exception:
            pass
        return

    anime = await db.get_anime_by_code(code)
    title = anime['title'] if anime else f"#{code}"
    await db.delete_anime(code)
    await call.answer(f"✅ {title} o'chirildi.")
    try:
        await call.message.delete()
    except Exception:
        pass
    kb = get_admin_anime_menu()
    await call.message.answer(f"✅ **{title}** va unga tegishli barcha qismlar muvaffaqiyatli o‘chirildi!", reply_markup=kb)
