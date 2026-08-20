from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from states.states import AdminChannelAdd
from keyboards.admin_kb import get_admin_channel_menu, get_admin_main_keyboard
from middlewares import normalize_channel_id

router = Router()

async def back_to_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "📢 Majburiy obuna")
async def msg_admin_channel_menu(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.clear()
    kb = get_admin_channel_menu()
    await message.answer("📢 **MAJBURIY OBUNA**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

# --- ADD CHANNEL ---
@router.message(F.text == "➕ Kanal qo‘shish")
async def cmd_add_channel_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.set_state(AdminChannelAdd.waiting_for_username)
    await message.answer("📢 Kanal username yoki ID'sini yuboring:\n(Masalan: `@anime_channel` yoki `-100123456789`)")

@router.message(AdminChannelAdd.waiting_for_username)
async def process_add_channel_username(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    ch_id = normalize_channel_id(text)
    await state.clear()

    await db.add_channel(ch_id, title=ch_id)
    kb = get_admin_channel_menu()
    await message.answer(f"✅ **Kanal muvaffaqiyatli qo‘shildi!**\n📢 `{ch_id}`", reply_markup=kb)

# --- LIST CHANNELS ---
@router.message(F.text == "📋 Kanallar ro‘yxati")
async def msg_list_channels(message: Message, is_admin: bool = False):
    if not is_admin:
        return
    channels = await db.get_channels()
    if not channels:
        await message.answer("📢 **MAJBURIY KANALLAR**\n\nHozircha kanallar yo'q.")
        return

    text = "📢 **MAJBURIY KANALLAR**\n\n"
    builder = InlineKeyboardBuilder()
    for idx, ch in enumerate(channels, start=1):
        text += f"{idx}. {ch['channel_id']}\n"
        builder.button(text=f"📢 {ch['channel_id']}", callback_data=f"adm_view_ch:{ch['id']}")
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("adm_view_ch:"))
async def callback_admin_view_channel(call: CallbackQuery):
    await call.answer()
    ch_id = int(call.data.split(":")[1])
    channels = await db.get_channels()
    target_ch = next((ch for ch in channels if ch['id'] == ch_id), None)

    if not target_ch:
        await call.answer("❌ Kanal topilmadi!", show_alert=True)
        return

    text = (
        f"📢 **{target_ch['channel_id']}**\n\n"
        f"Majburiy obuna: ✅"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 O‘chirish", callback_data=f"adm_del_ch:{target_ch['channel_id']}")
    builder.button(text="⬅️ Orqaga", callback_data="adm_back_channels")
    builder.adjust(1)

    await call.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "adm_back_channels")
async def callback_admin_back_channels(call: CallbackQuery, is_admin: bool = False):
    await call.answer()
    if not is_admin:
        return
    channels = await db.get_channels()
    if not channels:
        await call.message.edit_text("📢 **MAJBURIY KANALLAR**\n\nHozircha kanallar yo'q.")
        return

    text = "📢 **MAJBURIY KANALLAR**\n\n"
    builder = InlineKeyboardBuilder()
    for idx, ch in enumerate(channels, start=1):
        text += f"{idx}. {ch['channel_id']}\n"
        builder.button(text=f"📢 {ch['channel_id']}", callback_data=f"adm_view_ch:{ch['id']}")
    builder.adjust(1)
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- DELETE CHANNEL ---
@router.message(F.text == "🗑 Kanalni o‘chirish")
async def msg_del_channel_start(message: Message, is_admin: bool = False):
    if not is_admin:
        return
    channels = await db.get_channels()
    if not channels:
        await message.answer("❌ O'chirish uchun kanallar mavjud emas.")
        return

    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(text=f"🗑 {ch['channel_id']}", callback_data=f"adm_del_ch:{ch['channel_id']}")
    builder.adjust(1)

    await message.answer("🗑 O‘chirmoqchi bo'lgan kanalni tanlang:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("adm_del_ch:"))
async def callback_admin_del_channel(call: CallbackQuery):
    ch_id_str = call.data.split(":", 1)[1]
    await db.delete_channel(ch_id_str)
    await call.answer(f"✅ {ch_id_str} o'chirildi!")
    try:
        await call.message.delete()
    except Exception:
        pass
    kb = get_admin_channel_menu()
    await call.message.answer(f"✅ **{ch_id_str}** majburiy obuna ro'yxatidan o‘chirildi.", reply_markup=kb)
