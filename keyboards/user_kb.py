from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_main_keyboard(is_admin_user: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🔎 Anime qidirish"))
    builder.row(KeyboardButton(text="🔢 Kod orqali qidirish"))
    builder.row(KeyboardButton(text="📚 Anime katalogi"))
    if is_admin_user:
        builder.row(KeyboardButton(text="👨💻 Admin panel"))
    return builder.as_markup(resize_keyboard=True)

def get_sub_keyboard(channels, payload: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        ch_id = ch['channel_id']
        url = ch_id if ch_id.startswith("http") else f"https://t.me/{ch_id.replace('@', '')}"
        title = ch['title'] or ch_id
        builder.button(text=f"📢 {title}", url=url)
    
    check_cb = f"check_sub:{payload}" if payload else "check_sub:"
    builder.button(text="✅ Obunani tekshirish", callback_data=check_cb)
    builder.adjust(1)
    return builder.as_markup()

def get_anime_detail_keyboard(code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Qismlarni ko‘rish", callback_data=f"view_eps:{code}")
    builder.button(text="⬅️ Orqaga", callback_data="user_back_main")
    builder.adjust(1)
    return builder.as_markup()

def get_episodes_grid_keyboard(anime_code: str, episodes) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ep in episodes:
        ep_num = ep['episode_number']
        builder.button(text=f"{ep_num}-qism", callback_data=f"get_ep:{anime_code}:{ep_num}")
    
    # Grid: 3 per row
    builder.adjust(3)
    # Add Back button at the bottom
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"view_anime:{anime_code}"))
    return builder.as_markup()

def get_catalog_keyboard(animes, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, anime in enumerate(animes, start=1 + (current_page * 5)):
        builder.button(text=f"{index}. {anime['title']}", callback_data=f"view_anime:{anime['code']}")
    builder.adjust(1)
    
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"catalog_page:{current_page - 1}"))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"catalog_page:{current_page + 1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="user_back_main"))
    return builder.as_markup()
