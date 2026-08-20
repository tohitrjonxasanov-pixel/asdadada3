from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from keyboards.admin_kb import get_admin_main_keyboard, get_stats_keyboard
from keyboards.user_kb import get_main_keyboard

router = Router()

async def render_stats_text() -> str:
    total_users = await db.get_users_count()
    total_animes = await db.get_animes_count()
    total_episodes = await db.get_episodes_count()
    today_active = await db.get_today_active_users_count()
    today_new = await db.get_today_new_users_count()
    admins_count = await db.get_admins_count()
    channels_count = await db.get_channels_count()

    return (
        "📊 **BOT STATISTIKASI**\n\n"
        f"👥 Jami foydalanuvchilar: {total_users:,}\n"
        f"🎬 Jami anime: {total_animes:,}\n"
        f"📺 Jami qismlar: {total_episodes:,}\n\n"
        f"📅 Bugun kirganlar: {today_active:,}\n"
        f"📅 Bugun yangi foydalanuvchilar: {today_new:,}\n\n"
        f"👨💻 Adminlar: {admins_count:,}\n"
        f"📢 Majburiy kanallar: {channels_count:,}"
    )

@router.message(Command("admin"))
@router.message(F.text == "👨💻 Admin panel")
async def cmd_admin_panel(message: Message, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)

@router.message(F.text == "📊 Statistika")
async def msg_admin_stats(message: Message, is_admin: bool = False):
    if not is_admin:
        await message.answer("❌ Siz admin emassiz.")
        return
    text = await render_stats_text()
    kb = get_stats_keyboard()
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "refresh_stats")
async def callback_refresh_stats(call: CallbackQuery, is_admin: bool = False):
    if not is_admin:
        await call.answer("❌ Siz admin emassiz.", show_alert=True)
        return
    text = await render_stats_text()
    kb = get_stats_keyboard()
    try:
        await call.message.edit_text(text, reply_markup=kb)
        await call.answer("🔄 Statistika yangilandi!")
    except Exception:
        await call.answer("Statistika hozircha o'zgarmagan.")

@router.message(F.text == "🚪 Admin paneldan chiqish")
async def cmd_exit_admin_panel(message: Message, state: FSMContext, is_admin: bool = False):
    await state.clear()
    kb = get_main_keyboard(is_admin)
    await message.answer(
        "✅ Admin paneldan chiqildi.\n\n🏠 Oddiy foydalanuvchi menyusiga qaytdingiz.",
        reply_markup=kb
    )

@router.callback_query(F.data == "adm_back_main")
async def callback_admin_back_main(call: CallbackQuery, state: FSMContext, is_admin: bool = False):
    if not is_admin:
        await call.answer("❌ Siz admin emassiz.", show_alert=True)
        return
    await state.clear()
    try:
        await call.message.delete()
    except Exception:
        pass
    kb = get_admin_main_keyboard()
    await call.message.answer("👨💻 **ADMIN PANEL**\n\nKerakli bo‘limni tanlang:", reply_markup=kb)
