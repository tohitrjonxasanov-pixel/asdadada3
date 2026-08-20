import re
from typing import Tuple, Optional

_bot_username_cache = None

async def get_bot_username(bot) -> str:
    global _bot_username_cache
    if not _bot_username_cache:
        me = await bot.get_me()
        _bot_username_cache = me.username
    return _bot_username_cache

def generate_anime_link(bot_username: str, code: str) -> str:
    return f"https://t.me/{bot_username}?start={code}"

def generate_episode_link(bot_username: str, code: str, ep_num: int) -> str:
    ep_str = f"{ep_num:02d}" if ep_num < 10 else str(ep_num)
    return f"https://t.me/{bot_username}?start={code}_{ep_str}"

def parse_start_payload(payload: str) -> Tuple[Optional[str], Optional[int]]:
    if not payload or not payload.strip():
        return None, None
    payload = payload.strip()
    if "_" in payload:
        parts = payload.split("_")
        code = parts[0]
        try:
            ep_num = int(parts[1])
            return code, ep_num
        except ValueError:
            return code, None
    return payload, None

def format_anime_text(anime) -> str:
    # anime is a Row or Dict with title, genre, year, total_episodes, description, code
    code = anime['code'] if 'code' in anime.keys() else ""
    title = anime['title']
    genre = anime['genre'] or "Belgilanmagan"
    year = anime['year'] or "---"
    total_episodes = anime['total_episodes'] or 0
    description = anime['description'] or ""

    return (
        f"🎬 **{title}**\n\n"
        f"🎭 Janr: {genre}\n"
        f"📅 Yil: {year}\n"
        f"📺 Qismlar: {total_episodes}\n\n"
        f"📝 Tavsif:\n{description}"
    )

def format_anime_admin_text(anime, uploaded_count: int = 0) -> str:
    code = anime['code']
    title = anime['title']
    genre = anime['genre'] or "Belgilanmagan"
    year = anime['year'] or "---"
    total_episodes = anime['total_episodes'] or 0

    return (
        f"🎬 **{title}**\n\n"
        f"🔢 Kod: {code}\n"
        f"📺 Qismlar: {total_episodes}\n"
        f"📥 Yuklangan: {uploaded_count}\n"
        f"🎭 {genre}\n"
        f"📅 {year}"
    )
