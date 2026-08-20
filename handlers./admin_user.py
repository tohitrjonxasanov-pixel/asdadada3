from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from states.states import AdminUserSearch
from keyboards.admin_kb import get_admin_user_menu, get_admin_main_keyboard

router = Router()

async def back_to_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "👥 Foydalanuvchilar")
async def msg_admin_user_menu(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.clear()
    kb = get_admin_user_menu()
    await message.answer("👥 **FOYDALANUVCHILAR**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "👥 Jami foydalanuvchilar")
async def msg_total_users_count(message: Message, is_admin: bool = False):
    if not is_admin:
        return
    count = await db.get_users_count()
    await message.answer(f"👥 **Jami foydalanuvchilar:** {count:,} ta")

# --- SEARCH USER BY ID ---
@router.message(F.text == "🔎 Foydalanuvchi qidirish")
async def cmd_search_user_start(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    await state.set_state(AdminUserSearch.waiting_for_user_id)
    await message.answer("🆔 Foydalanuvchining Telegram ID'sini yuboring:")

@router.message(AdminUserSearch.waiting_for_user_id)
async def process_search_user_id(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    try:
        target_id = int(text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat sonli Telegram ID yuboring (masalan: 123456789):")
        return

    await state.clear()
    user_row = await db.get_user(target_id)
    if not user_row:
        await message.answer(f"❌ **{target_id}** ID'li foydalanuvchi bazadan topilmadi.")
        return

    status_str = "Bloklangan 🚫" if user_row['is_blocked'] else "Faol 🟢"
    reg_date = user_row['joined_at'] or "---"
    watched = user_row['episodes_watched'] or 0

    text_card = (
        f"👤 **FOYDALANUVCHI**\n\n"
        f"🆔 ID: `{user_row['user_id']}`\n"
        f"👤 Ism: {user_row['full_name'] or '---'}\n"
        f"🔗 Username: @{user_row['username'] or '---'}\n"
        f"📅 Ro‘yxatdan o‘tgan: {reg_date}\n"
        f"📺 Ko‘rilgan qismlar: {watched}\n"
        f"🚫 Holati: {status_str}"
    )

    builder = InlineKeyboardBuilder()
    block_btn_text = "🟢 Blokdan chiqarish" if user_row['is_blocked'] else "🚫 Bloklash"
    builder.button(text=block_btn_text, callback_data=f"adm_toggle_block:{user_row['user_id']}")
    builder.button(text="📩 Xabar yuborish", callback_data=f"adm_msg_user:{user_row['user_id']}")
    builder.button(text="⬅️ Orqaga", callback_data="adm_back_user_menu")
    builder.adjust(1)

    await message.answer(text_card, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("adm_toggle_block:"))
async def callback_toggle_user_block(call: CallbackQuery, is_admin: bool = False):
    if not is_admin:
        return
    target_id = int(call.data.split(":")[1])
    user_row = await db.get_user(target_id)
    if not user_row:
        await call.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return

    new_status = not bool(user_row['is_blocked'])
    await db.set_user_blocked(target_id, new_status)
    action_str = "bloklandi" if new_status else "blokdan chiqarildi"
    await call.answer(f"Foydalanuvchi {action_str}!")

    # Refresh card
    updated_user = await db.get_user(target_id)
    status_str = "Bloklangan 🚫" if updated_user['is_blocked'] else "Faol 🟢"
    text_card = (
        f"👤 **FOYDALANUVCHI**\n\n"
        f"🆔 ID: `{updated_user['user_id']}`\n"
        f"👤 Ism: {updated_user['full_name'] or '---'}\n"
        f"🔗 Username: @{updated_user['username'] or '---'}\n"
        f"📅 Ro‘yxatdan o‘tgan: {updated_user['joined_at'] or '---'}\n"
        f"📺 Ko‘rilgan qismlar: {updated_user['episodes_watched'] or 0}\n"
        f"🚫 Holati: {status_str}"
    )
    builder = InlineKeyboardBuilder()
    block_btn_text = "🟢 Blokdan chiqarish" if updated_user['is_blocked'] else "🚫 Bloklash"
    builder.button(text=block_btn_text, callback_data=f"adm_toggle_block:{updated_user['user_id']}")
    builder.button(text="📩 Xabar yuborish", callback_data=f"adm_msg_user:{updated_user['user_id']}")
    builder.button(text="⬅️ Orqaga", callback_data="adm_back_user_menu")
    builder.adjust(1)

    try:
        await call.message.edit_text(text_card, reply_markup=builder.as_markup())
    except Exception:
        pass

@router.callback_query(F.data.startswith("adm_msg_user:"))
async def callback_send_msg_user_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    target_id = int(call.data.split(":")[1])
    await state.set_state(AdminUserSearch.waiting_for_message)
    await state.update_data(target_user_id=target_id)
    await call.message.answer(f"📩 `{target_id}` ID'li foydalanuvchiga yubormoqchi bo'lgan xabaringizni yuboring:")

@router.message(AdminUserSearch.waiting_for_message)
async def process_send_msg_user(message: Message, state: FSMContext, bot):
    if message.text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    data = await state.get_data()
    target_id = data.get("target_user_id")
    await state.clear()

    if not target_id:
        await message.answer("❌ Xatolik: foydalanuvchi ID topilmadi.")
        return

    try:
        await bot.send_message(chat_id=target_id, text=f"📩 **ADMIN XABARI:**\n\n{message.text}")
        await message.answer(f"✅ Xabar `{target_id}` ID'li foydalanuvchiga muvaffaqiyatli yuborildi!")
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xatolik yuz berdi: {e}")

@router.callback_query(F.data == "adm_back_user_menu")
async def callback_admin_back_user_menu(call: CallbackQuery, is_admin: bool = False):
    await call.answer()
    if not is_admin:
        return
    try:
        await call.message.delete()
    except Exception:
        pass
    kb = get_admin_user_menu()
    await call.message.answer("👥 **FOYDALANUVCHILAR**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)
