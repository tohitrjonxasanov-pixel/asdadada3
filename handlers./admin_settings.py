from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from config import SUPER_ADMIN_ID
from states.states import AdminSettingsEdit, AdminAddState
from keyboards.admin_kb import get_admin_settings_menu, get_admin_admins_menu, get_admin_main_keyboard
from utils.helpers import get_bot_username

router = Router()

async def back_to_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

# --- SETTINGS MENU ---
@router.message(F.text == "⚙️ Sozlamalar")
async def msg_admin_settings_menu(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.clear()
    kb = get_admin_settings_menu()
    await message.answer("⚙️ **SOZLAMALAR**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "✏️ Start xabarini o‘zgartirish")
async def cmd_edit_start_text(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    current = await db.get_setting("start_text", "")
    await state.set_state(AdminSettingsEdit.waiting_for_start_text)
    await message.answer(f"⚙️ **Hozirgi /start xabari:**\n\n{current}\n\n✏️ Yangi xabarni yuboring:")

@router.message(AdminSettingsEdit.waiting_for_start_text)
async def process_edit_start_text(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    new_text = message.text.strip()
    await db.set_setting("start_text", new_text)
    await state.clear()
    kb = get_admin_settings_menu()
    await message.answer("✅ **/start xabari muvaffaqiyatli yangilandi!**", reply_markup=kb)

@router.message(F.text == "✏️ Obuna xabarini o‘zgartirish")
async def cmd_edit_sub_text(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        return
    current = await db.get_setting("sub_text", "")
    await state.set_state(AdminSettingsEdit.waiting_for_sub_text)
    await message.answer(f"⚙️ **Hozirgi obuna xabari:**\n\n{current}\n\n✏️ Yangi obuna matnini yuboring:")

@router.message(AdminSettingsEdit.waiting_for_sub_text)
async def process_edit_sub_text(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    new_text = message.text.strip()
    await db.set_setting("sub_text", new_text)
    await state.clear()
    kb = get_admin_settings_menu()
    await message.answer("✅ **Obuna matni muvaffaqiyatli yangilandi!**", reply_markup=kb)

@router.message(F.text == "🔗 Bot username")
async def cmd_view_bot_username(message: Message, bot, is_admin: bool = False):
    if not is_admin:
        return
    username = await get_bot_username(bot)
    await message.answer(f"🔗 **Bot Username:** @{username}\n\nLink: https://t.me/{username}")

# --- ADMINS MANAGEMENT (SUPERADMIN ONLY) ---
@router.message(F.text == "👨💻 Adminlar")
async def msg_admin_admins_menu(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("❌ Bu bo'lim faqat Asosiy Admin uchun ochiq!")
        return
    await state.clear()
    kb = get_admin_admins_menu()
    await message.answer("👨💻 **ADMINLAR BOSHQARUVI**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "➕ Admin qo‘shish")
async def cmd_add_admin_start(message: Message, state: FSMContext):
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    await state.set_state(AdminAddState.waiting_for_admin_id)
    await message.answer("🆔 Adminning Telegram ID'sini yuboring:")

@router.message(AdminAddState.waiting_for_admin_id)
async def process_add_admin_id(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if text == "⬅️ Orqaga":
        await back_to_admin_panel(message, state)
        return

    try:
        new_admin_id = int(text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqamli Telegram ID yuboring:")
        return

    await state.clear()
    await db.add_admin(new_admin_id)
    kb = get_admin_admins_menu()
    await message.answer(f"✅ **Admin qo‘shildi.**\n\nEndi u /admin orqali panelga kira oladi.", reply_markup=kb)

@router.message(F.text == "📋 Adminlar")
async def msg_list_admins(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        return

    admins = await db.get_all_admins()
    text = "👨💻 **ADMINLAR RO'YXATI**\n\n"
    builder = InlineKeyboardBuilder()

    for idx, adm in enumerate(admins, start=1):
        adm_id = adm['user_id']
        role = "(Bosh admin)" if adm_id == SUPER_ADMIN_ID else ""
        text += f"{idx}. `{adm_id}` {role}\n"
        if adm_id != SUPER_ADMIN_ID:
            builder.button(text=f"🗑 `{adm_id}` ni o'chirish", callback_data=f"adm_del_admin:{adm_id}")

    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup() if builder.buttons else None)

@router.message(F.text == "🗑 Adminni o‘chirish")
async def msg_del_admin_prompt(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        return

    admins = await db.get_all_admins()
    builder = InlineKeyboardBuilder()
    for adm in admins:
        adm_id = adm['user_id']
        if adm_id != SUPER_ADMIN_ID:
            builder.button(text=f"🗑 `{adm_id}`", callback_data=f"adm_del_admin:{adm_id}")
    builder.adjust(1)

    if not builder.buttons:
        await message.answer("❌ O'chirish mumkin bo'lgan qo'shimcha adminlar yo'q.")
        return

    await message.answer("🗑 O'chirmoqchi bo'lgan adminingizni tanlang:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("adm_del_admin:"))
async def callback_delete_admin(call: CallbackQuery):
    if call.from_user.id != SUPER_ADMIN_ID:
        await call.answer("❌ Faqat Asosiy Admin buni bajara oladi!", show_alert=True)
        return

    target_id = int(call.data.split(":")[1])
    success = await db.remove_admin(target_id)
    if success:
        await call.answer(f"✅ Admin {target_id} o'chirildi!")
        try:
            await call.message.delete()
        except Exception:
            pass
        kb = get_admin_admins_menu()
        await call.message.answer(f"✅ `{target_id}` adminlik huquqidan mahrum qilindi.", reply_markup=kb)
    else:
        await call.answer("❌ Bosh adminni o'chirib bo'lmaydi!", show_alert=True)
