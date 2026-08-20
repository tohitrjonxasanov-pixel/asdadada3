import aiosqlite
import datetime
from config import DB_PATH, SUPER_ADMIN_ID, DEFAULT_START_TEXT, DEFAULT_SUB_TEXT

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                joined_at TEXT,
                last_active TEXT,
                episodes_watched INTEGER DEFAULT 0,
                is_blocked INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS animes (
                code TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                poster_file_id TEXT,
                genre TEXT,
                year INTEGER,
                total_episodes INTEGER,
                description TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_code TEXT NOT NULL,
                episode_number INTEGER NOT NULL,
                video_file_id TEXT NOT NULL,
                created_at TEXT,
                UNIQUE(anime_code, episode_number),
                FOREIGN KEY (anime_code) REFERENCES animes (code) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE NOT NULL,
                title TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                added_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Add superadmin if not present
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute("INSERT OR IGNORE INTO admins (user_id, added_at) VALUES (?, ?)", (SUPER_ADMIN_ID, now_str))
        
        # Seed default settings
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('start_text', ?)", (DEFAULT_START_TEXT,))
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('sub_text', ?)", (DEFAULT_SUB_TEXT,))
        
        await db.commit()

# --- USER FUNCTIONS ---
async def add_or_update_user(user_id: int, full_name: str, username: str):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                await db.execute(
                    "UPDATE users SET full_name = ?, username = ?, last_active = ? WHERE user_id = ?",
                    (full_name, username, now_str, user_id)
                )
            else:
                await db.execute(
                    "INSERT INTO users (user_id, full_name, username, joined_at, last_active) VALUES (?, ?, ?, ?, ?)",
                    (user_id, full_name, username, now_str, now_str)
                )
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_today_active_users_count():
    today_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE last_active LIKE ?", (f"{today_prefix}%",)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_today_new_users_count():
    today_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE joined_at LIKE ?", (f"{today_prefix}%",)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def set_user_blocked(user_id: int, is_blocked: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_blocked = ? WHERE user_id = ?", (1 if is_blocked else 0, user_id))
        await db.commit()

async def increment_user_episodes(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET episodes_watched = episodes_watched + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

# --- ANIME FUNCTIONS ---
async def get_next_anime_code() -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT code FROM animes") as cursor:
            rows = await cursor.fetchall()
            max_num = 0
            for r in rows:
                try:
                    num = int(r[0])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
            next_num = max_num + 1
            if next_num < 100:
                return f"{next_num:03d}"
            return str(next_num)

async def add_anime(code: str, title: str, poster_file_id: str, genre: str, year: int, total_episodes: int, description: str):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO animes (code, title, poster_file_id, genre, year, total_episodes, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (code, title, poster_file_id, genre, year, total_episodes, description, now_str)
        )
        await db.commit()

async def get_anime_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes WHERE code = ?", (code,)) as cursor:
            return await cursor.fetchone()

async def search_anime_by_title(query: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes WHERE LOWER(title) LIKE LOWER(?) ORDER BY title ASC", (f"%{query}%",)) as cursor:
            return await cursor.fetchall()

async def get_all_animes(limit: int = 10, offset: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes ORDER BY title ASC LIMIT ? OFFSET ?", (limit, offset)) as cursor:
            return await cursor.fetchall()

async def get_animes_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM animes") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def update_anime_field(code: str, field: str, value):
    valid_fields = ["title", "poster_file_id", "genre", "year", "total_episodes", "description"]
    if field not in valid_fields:
        raise ValueError("Invalid field")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE animes SET {field} = ? WHERE code = ?", (value, code))
        await db.commit()

async def delete_anime(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM episodes WHERE anime_code = ?", (code,))
        await db.execute("DELETE FROM animes WHERE code = ?", (code,))
        await db.commit()

# --- EPISODE FUNCTIONS ---
async def add_episode(anime_code: str, episode_number: int, video_file_id: str):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO episodes (anime_code, episode_number, video_file_id, created_at) VALUES (?, ?, ?, ?)",
            (anime_code, episode_number, video_file_id, now_str)
        )
        await db.commit()

async def get_episode(anime_code: str, episode_number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM episodes WHERE anime_code = ? AND episode_number = ?", (anime_code, episode_number)) as cursor:
            return await cursor.fetchone()

async def get_episodes_by_anime(anime_code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM episodes WHERE anime_code = ? ORDER BY episode_number ASC", (anime_code,)) as cursor:
            return await cursor.fetchall()

async def get_episodes_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM episodes") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def update_episode_video(anime_code: str, episode_number: int, video_file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE episodes SET video_file_id = ? WHERE anime_code = ? AND episode_number = ?", (video_file_id, anime_code, episode_number))
        await db.commit()

async def update_episode_number(anime_code: str, old_number: int, new_number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE episodes SET episode_number = ? WHERE anime_code = ? AND episode_number = ?", (new_number, anime_code, old_number))
        await db.commit()

async def delete_episode(anime_code: str, episode_number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM episodes WHERE anime_code = ? AND episode_number = ?", (anime_code, episode_number))
        await db.commit()

# --- CHANNEL FUNCTIONS ---
async def add_channel(channel_id: str, title: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO channels (channel_id, title) VALUES (?, ?)", (channel_id, title))
        await db.commit()

async def get_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM channels WHERE is_active = 1") as cursor:
            return await cursor.fetchall()

async def delete_channel(channel_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        await db.commit()

async def get_channels_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# --- ADMIN FUNCTIONS ---
async def add_admin(user_id: int):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO admins (user_id, added_at) VALUES (?, ?)", (user_id, now_str))
        await db.commit()

async def remove_admin(user_id: int):
    if user_id == SUPER_ADMIN_ID:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        await db.commit()
    return True

async def is_admin(user_id: int) -> bool:
    if user_id == SUPER_ADMIN_ID:
        return True
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def get_all_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM admins") as cursor:
            return await cursor.fetchall()

async def get_admins_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM admins") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

# --- SETTINGS FUNCTIONS ---
async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()
