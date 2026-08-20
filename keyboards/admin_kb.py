
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📊 Statistika"))
    builder.row(KeyboardButton(text="🎬 Anime boshqarish"))
    builder.row(KeyboardButton(text="📺 Qismlar boshqarish"))
    builder.row(KeyboardButton(text="📢 Majburiy obuna"))
    builder.row(KeyboardButton(text="👥 Foydalanuvchilar"))
    builder.row(KeyboardButton(text="👨💻 Adminlar"))
    builder.row(KeyboardButton(text="⚙️ Sozlamalar"))
    builder.row(KeyboardButton(text="🚪 Admin paneldan chiqish"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_anime_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Anime qo‘shish"))
    builder.row(KeyboardButton(text="📋 Anime ro‘yxati"))
    builder.row(KeyboardButton(text="🔎 Anime qidirish"))
    builder.row(KeyboardButton(text="✏️ Anime tahrirlash"))
    builder.row(KeyboardButton(text="🗑 Anime o‘chirish"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_episode_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Qism qo‘shish"))
    builder.row(KeyboardButton(text="✏️ Qismni tahrirlash"))
    builder.row(KeyboardButton(text="🗑 Qismni o‘chirish"))
    builder.row(KeyboardButton(text="📋 Qismlar ro‘yxati"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_channel_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Kanal qo‘shish"))
    builder.row(KeyboardButton(text="📋 Kanallar ro‘yxati"))
    builder.row(KeyboardButton(text="🗑 Kanalni o‘chirish"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_user_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="👥 Jami foydalanuvchilar"))
    builder.row(KeyboardButton(text="🔎 Foydalanuvchi qidirish"))
    builder.row(KeyboardButton(text="🚫 Bloklanganlar"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_admins_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Admin qo‘shish"))
    builder.row(KeyboardButton(text="📋 Adminlar"))
    builder.row(KeyboardButton(text="🗑 Adminni o‘chirish"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_settings_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✏️ Start xabarini o‘zgartirish"))
    builder.row(KeyboardButton(text="✏️ Obuna xabarini o‘zgartirish"))
    builder.row(KeyboardButton(text="🔗 Bot username"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

# Inline Keyboards for Admin Detail Views
def get_admin_anime_detail_keyboard(code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📺 Qismlar", callback_data=f"adm_eps:{code}")
    builder.button(text="➕ Qism qo‘shish", callback_data=f"adm_add_ep:{code}")
    builder.button(text="✏️ Tahrirlash", callback_data=f"adm_edit_anime:{code}")
    builder.button(text="🗑 O‘chirish", callback_data=f"adm_del_anime:{code}")
    builder.button(text="🔗 Link", callback_data=f"adm_link_anime:{code}")
    builder.button(text="⬅️ Orqaga", callback_data="adm_anime_list:0")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()

def get_admin_anime_edit_fields_keyboard(code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Nom", callback_data=f"edit_field:{code}:title")
    builder.button(text="🖼 Poster", callback_data=f"edit_field:{code}:poster_file_id")
    builder.button(text="🎭 Janr", callback_data=f"edit_field:{code}:genre")
    builder.button(text="📅 Yil", callback_data=f"edit_field:{code}:year")
    builder.button(text="📺 Qism soni", callback_data=f"edit_field:{code}:total_episodes")
    builder.button(text="📝 Tavsif", callback_data=f"edit_field:{code}:description")
    builder.button(text="⬅️ Orqaga", callback_data=f"adm_view_anime:{code}")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()

def get_confirm_keyboard(action_prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Saqlash", callback_data=f"{action_prefix}_yes")
    builder.button(text="❌ Bekor qilish", callback_data=f"{action_prefix}_no")
    builder.adjust(2)
    return builder.as_markup()

def get_delete_confirm_keyboard(action_prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Ha, o‘chirish", callback_data=f"{action_prefix}_yes")
    builder.button(text="❌ Bekor qilish", callback_data=f"{action_prefix}_no")
    builder.adjust(2)
    return builder.as_markup()

def get_stats_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Yangilash", callback_data="refresh_stats")
    builder.button(text="⬅️ Orqaga", callback_data="adm_back_main")
    builder.adjust(1)
    return builder.as_markup()
