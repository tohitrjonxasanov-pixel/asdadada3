from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from states.states import AdminEpisodeAdd, AdminEpisodeEdit
from keyboards.admin_kb import (
    get_admin_episode_menu,
    get_admin_main_keyboard,
    get_delete_confirm_keyboard
)
from utils.helpers import get_bot_username, generate_episode_link

router = Router()

async def back_to_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "📺 Qismlar boshqarish")
async def msg_admin_episode_menu(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.clear()
    kb = get_admin_episode_menu()
    await message.answer("📺 **QISMLAR BOSHQARISH**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

# --- ADD EPISODE ---
@router.message(F.text == "➕ Qism qo‘shish")
@router.callback_query(F.data.startswith("adm_add_ep:"))
async def cmd_add_episode_start(message_or_call: Message | CallbackQuery, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    
    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.answer()
        code = message_or_call.data.split(":")[1]
        anime = await db.get_anime_by_code(code)
        if not anime:
            await message_or_call.answer("❌ Anime topilmadi!", show_alert=True)
            return
        await state.set_state(AdminEpisodeAdd.waiting_for_number)
        await state.update_data(code=code)
        await message_or_call.message.answer(f"🎬 **{anime['title']}**\n\n📺 Qism raqamini yuboring:")
        return

    await state.set_state(AdminEpisodeAdd.waiting_for_code)
    await message_or_call.answer("🔢 Anime kodini yuboring:")

@router.message(AdminEpisodeAdd.waiting_for_code)
async def process_add_episode_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if code == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    anime = await db.get_anime_by_code(code)
    if not anime:
        await message.answer(f"❌ **{code}** kodli anime topilmadi! Qaytadan kodni yuboring:")
        return

    await state.update_data(code=code)
    await state.set_state(AdminEpisodeAdd.waiting_for_number)
    await message.answer(f"🎬 **{anime['title']}**\n\n📺 Qism raqamini yuboring:")

@router.message(AdminEpisodeAdd.waiting_for_number)
async def process_add_episode_number(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    try:
        ep_num = int(text)
    except ValueError:
        await message.answer("❌ Iltimos, qism raqamini son ko'rinishida yuboring (masalan: 4):")
        return

    data = await state.get_data()
    code = data['code']
    anime = await db.get_anime_by_code(code)

    await state.update_data(ep_num=ep_num)
    await state.set_state(AdminEpisodeAdd.waiting_for_video)
    await message.answer(f"🎥 **{anime['title']} — {ep_num}-qism** videosini yuboring:")

@router.message(AdminEpisodeAdd.waiting_for_video)
async def process_add_episode_video(message: Message, state: FSMContext, bot):
    if message.text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    if not message.video:
        await message.answer("❌ Iltimos, videoni fayl/video shaklida yuboring:")
        return

    video_id = message.video.file_id
    data = await state.get_data()
    code = data['code']
    ep_num = data['ep_num']
    await state.clear()

    anime = await db.get_anime_by_code(code)
    await db.add_episode(code, ep_num, video_id)

    bot_username = await get_bot_username(bot)
    ep_link = generate_episode_link(bot_username, code, ep_num)

    success_text = (
        f"✅ **{ep_num}-qism muvaffaqiyatli qo‘shildi!**\n\n"
        f"🎬 Anime: {anime['title'] if anime else code}\n"
        f"📺 Qism: {ep_num}\n\n"
        f"🔗 Qism linki:\n{ep_link}"
    )
    kb = get_admin_episode_menu()
    await message.answer(success_text, reply_markup=kb)

# --- LIST EPISODES STATUS ---
@router.message(F.text == "📋 Qismlar ro‘yxati")
@router.callback_query(F.data.startswith("adm_eps:"))
async def cmd_list_episodes_start(message_or_call: Message | CallbackQuery, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.answer()
        code = message_or_call.data.split(":")[1]
        await render_admin_episodes_list(message_or_call, code)
        return

    await state.set_state(AdminEpisodeEdit.waiting_for_code)
    await state.update_data(target_action="list")
    await message_or_call.answer("🔢 Anime kodini yuboring:")

async def render_admin_episodes_list(message_or_call, code: str):
    anime = await db.get_anime_by_code(code)
    if not anime:
        text = f"❌ **{code}** kodli anime topilmadi!"
        if isinstance(message_or_call, Message):
            await message_or_call.answer(text)
        else:
            await message_or_call.message.answer(text)
        return

    episodes = await db.get_episodes_by_anime(code)
    uploaded_dict = {ep['episode_number']: ep for ep in episodes}
    total_eps = anime['total_episodes'] or max(uploaded_dict.keys(), default=1)

    builder = InlineKeyboardBuilder()
    for ep_n in range(1, total_eps + 1):
        has = ep_n in uploaded_dict
        status = "✅" if has else "❌"
        builder.button(text=f"{ep_n}-qism {status}", callback_data=f"adm_ep_detail:{code}:{ep_n}")
    builder.adjust(2)
    builder.row(InlineKeyboardBuilder().button(text="⬅️ Orqaga", callback_data=f"adm_view_anime:{code}").buttons[0])

    text = f"🎬 **{anime['title']}**\n\n📺 **QISMLAR:**\n✅ — video yuklangan, ❌ — hali video yo‘q."
    if isinstance(message_or_call, Message):
        await message_or_call.answer(text, reply_markup=builder.as_markup())
    else:
        try:
            await message_or_call.message.edit_text(text, reply_markup=builder.as_markup())
        except Exception:
            await message_or_call.message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("adm_ep_detail:"))
async def callback_admin_ep_detail(call: CallbackQuery, bot):
    await call.answer()
    parts = call.data.split(":")
    code = parts[1]
    ep_num = int(parts[2])

    anime = await db.get_anime_by_code(code)
    episode = await db.get_episode(code, ep_num)
    bot_username = await get_bot_username(bot)

    has_video = "mavjud" if episode else "yo'q"
    link = generate_episode_link(bot_username, code, ep_num) if episode else "mavjud emas"

    text = (
        f"📺 **{anime['title'] if anime else code} — {ep_num}-qism**\n\n"
        f"🎥 Video: {has_video}\n"
        f"🔗 Link: `{link}`"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Tahrirlash", callback_data=f"ep_action:{code}:{ep_num}:select")
    builder.button(text="🗑 O‘chirish", callback_data=f"adm_del_ep:{code}:{ep_num}")
    builder.button(text="⬅️ Orqaga", callback_data=f"adm_eps:{code}")
    builder.adjust(2, 1)

    try:
        await call.message.edit_text(text, reply_markup=builder.as_markup())
    except Exception:
        await call.message.answer(text, reply_markup=builder.as_markup())

# --- EDIT EPISODE ---
@router.message(F.text == "✏️ Qismni tahrirlash")
async def msg_admin_edit_ep_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.set_state(AdminEpisodeEdit.waiting_for_code)
    await state.update_data(target_action="edit")
    await message.answer("🔢 Anime kodini yuboring:")

@router.callback_query(F.data.startswith("ep_action:"))
async def callback_ep_action_select(call: CallbackQuery, state: FSMContext):
    await call.answer()
    parts = call.data.split(":")
    code = parts[1]
    ep_num = int(parts[2])
    action = parts[3]

    anime = await db.get_anime_by_code(code)
    if action == "select":
        builder = InlineKeyboardBuilder()
        builder.button(text="🎥 Videoni almashtirish", callback_data=f"ep_action:{code}:{ep_num}:video")
        builder.button(text="🔢 Qism raqamini o‘zgartirish", callback_data=f"ep_action:{code}:{ep_num}:number")
        builder.button(text="⬅️ Orqaga", callback_data=f"adm_ep_detail:{code}:{ep_num}")
        builder.adjust(1)

        text = f"📺 **{anime['title'] if anime else code} — {ep_num}-qism**\n\nNimani o‘zgartirasiz?"
        await call.message.edit_text(text, reply_markup=builder.as_markup())
        return

    if action == "video":
        await state.set_state(AdminEpisodeEdit.waiting_for_new_video)
        await state.update_data(edit_code=code, edit_ep_num=ep_num)
        await call.message.answer(f"🎥 **{ep_num}-qism** uchun yangi videoni yuboring:")
        return

    if action == "number":
        await state.set_state(AdminEpisodeEdit.waiting_for_new_number)
        await state.update_data(edit_code=code, edit_ep_num=ep_num)
        await call.message.answer(f"🔢 **{ep_num}-qism** uchun yangi qism raqamini yuboring:")
        return

@router.message(AdminEpisodeEdit.waiting_for_new_video)
async def process_edit_ep_new_video(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    if not message.video:
        await message.answer("❌ Iltimos, videoni yuboring:")
        return

    data = await state.get_data()
    code = data['edit_code']
    ep_num = data['edit_ep_num']
    await state.clear()

    await db.update_episode_video(code, ep_num, message.video.file_id)
    await message.answer(f"✅ **{ep_num}-qism** videosi muvaffaqiyatli almashtirildi!")

@router.message(AdminEpisodeEdit.waiting_for_new_number)
async def process_edit_ep_new_number(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    try:
        new_num = int(text)
    except ValueError:
        await message.answer("❌ Iltimos, raqam yuboring:")
        return

    data = await state.get_data()
    code = data['edit_code']
    old_num = data['edit_ep_num']
    await state.clear()

    existing = await db.get_episode(code, new_num)
    if existing and new_num != old_num:
        await message.answer(f"❌ **{new_num}-qism** allaqachon mavjud! Amal bekor qilindi.")
        return

    await db.update_episode_number(code, old_num, new_num)
    await message.answer(f"✅ Qism raqami **{old_num} -> {new_num}** ga o'zgartirildi!")

# --- DELETE EPISODE ---
@router.message(F.text == "🗑 Qismni o‘chirish")
async def msg_admin_del_ep_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.set_state(AdminEpisodeEdit.waiting_for_code)
    await state.update_data(target_action="delete")
    await message.answer("🔢 Anime kodini yuboring:")

@router.callback_query(F.data.startswith("adm_del_ep:"))
async def callback_admin_del_ep(call: CallbackQuery):
    await call.answer()
    parts = call.data.split(":")
    code = parts[1]
    ep_num = int(parts[2])

    anime = await db.get_anime_by_code(code)
    text = (
        f"⚠️ **{ep_num}-qismni o‘chirmoqchimisiz?**\n\n"
        f"🎬 Anime: {anime['title'] if anime else code}\n"
        f"📺 Qism: {ep_num}"
    )
    kb = get_delete_confirm_keyboard(f"confirm_del_ep:{code}:{ep_num}")
    await call.message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("confirm_del_ep:"))
async def process_confirm_delete_ep(call: CallbackQuery):
    parts = call.data.split(":")
    code = parts[1]
    ep_num = int(parts[2])
    action = parts[3]

    if action == "no":
        await call.answer("O'chirish bekor qilindi.")
        try:
            await call.message.delete()
        except Exception:
            pass
        return

    await db.delete_episode(code, ep_num)
    await call.answer("✅ Qism o'chirildi.")
    try:
        await call.message.delete()
    except Exception:
        pass
    kb = get_admin_episode_menu()
    await call.message.answer(f"✅ **{ep_num}-qism** o‘chirildi.", reply_markup=kb)

# --- FSM ROUTER FOR ANIME CODE INPUT IN EPISODES ---
@router.message(AdminEpisodeEdit.waiting_for_code)
async def process_ep_action_code_input(message: Message, state: FSMContext):
    code = message.text.strip()
    if code == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    data = await state.get_data()
    target_action = data.get("target_action", "list")
    await state.clear()

    anime = await db.get_anime_by_code(code)
    if not anime:
        await message.answer(f"❌ **{code}** kodli anime topilmadi!")
        return

    if target_action == "list":
        await render_admin_episodes_list(message, code)
    else:
        episodes = await db.get_episodes_by_anime(code)
        if not episodes:
            await message.answer(f"❌ **{anime['title']}** uchun qismlar topilmadi.")
            return

        builder = InlineKeyboardBuilder()
        for ep in episodes:
            ep_n = ep['episode_number']
            cb_data = f"ep_action:{code}:{ep_n}:select" if target_action == "edit" else f"adm_del_ep:{code}:{ep_n}"
            builder.button(text=f"{ep_n}-qism", callback_data=cb_data)
        builder.adjust(3)

        text = f"🎬 **{anime['title']}**\nQaysi qismni tanlaysiz?"
        await message.answer(text, reply_markup=builder.as_markup())
