# 🎬 Anime Telegram Bot (Uzbek Language)

Mukammal tuzilmali, tezkor va xavfsiz **Anime Telegram Boti**. Ushbu bot **Python 3.12**, **Aiogram 3.x** va **Async SQLite (aiosqlite)** arxitekturasida yaratilgan.

---

## 🌟 Xususiyatlari

### 👤 Foydalanuvchilar uchun:
1. **Majburiy Obuna Tizimi**:
   - `/start` bosilganda bot foydalanuvchini bazaga qo'shadi va majburiy kanallarga obunasini tekshiradi.
   - Kanallarga obuna bo'linmaguncha kontent va videolarga kirish cheklanadi.
   - Deep-link (`/start 125` yoki `/start 125_04`) orqali kirilganda ham obuna tekshirilib, obunadan so'ng avtomatik anime yoki videoni yuboradi.

2. **Asosiy Menyular**:
   - **🔎 Anime qidirish**: Anime nomini yozish orqali bazadan qidirish.
   - **🔢 Kod orqali qidirish**: Anime maxsus kodi (masalan, `125`) orqali tezkor topish.
   - **📚 Anime katalogi**: Barcha animelarning sahifalangan (pagination) tugmali ro'yxati.

3. **Anime va Qismlarni ko'rish**:
   - Poster, Janr, Yil, Qismlar soni hamda Tavsifi ko'rsatiladi.
   - **▶️ Qismlarni ko'rish** tugmasi orqali faqat **yuklangan/mavjud qismlar** tugma shaklida chiqadi.
   - Qism bosilganda Telegram videoni to'g'ridan-to'g'ri sifatli caption bilan yuboradi.

---

### 👨💻 Admin Panel (`/admin`):
1. **📊 Statistika**:
   - Jami foydalanuvchilar, Jami anime, Jami qismlar.
   - Bugun kirgan va yangi qo'shilgan foydalanuvchilar soni.
   - Adminlar va majburiy kanallar soni + `[🔄 Yangilash]` tugmasi.

2. **🎬 Anime boshqarish**:
   - **➕ Anime qo'shish**: Qadam-baqadam (Nom -> Poster -> Janr -> Yil -> Qismlar soni -> Tavsif -> Tasdiqlash) FSM masteri. Avtomatik unikal kod va Deep-Link yaratish.
   - **📋 Anime ro'yxati**: Animelarni boshqarish dashboardi.
   - **🔎 Anime qidirish** & **✏️ Anime tahrirlash** (Nom, Poster, Janr, Yil, Tavsif, Qismlar soni).
   - **🗑 Anime o'chirish**: O'chirishdan oldin xavfsizlik tasdiqnomasi.

3. **📺 Qismlar boshqarish**:
   - **➕ Qism qo'shish**: Anime kodi + Qism raqami + Video fayli -> Avtomatik qism deep-link (`https://t.me/Bot?start=125_04`).
   - **✏️ Qism tahrirlash**: Video almashtirish yoki qism raqamini o'zgartirish.
   - **📋 Qismlar ro'yxati**: Barcha qismlarning `✅ Yuklangan` / `❌ Yo'q` holatlari ro'yxati.

4. **📢 Majburiy obuna boshqarish**:
   - **➕ Kanal qo'shish** (`@username` yoki ID).
   - **📋 Kanallar ro'yxati** va **🗑 Kanalni o'chirish**.

5. **👥 Foydalanuvchilar boshqarish**:
   - Telegram ID bo'yicha foydalanuvchi profilini ko'rish (Ro'yxatdan o'tgan sana, ko'rilgan qismlar).
   - **🚫 Bloklash / Blokdan chiqarish**.
   - **📩 Xabar yuborish** (Foydalanuvchiga to'g'ridan-to mehmondust xabar yuborish).

6. **👨💻 Adminlar**:
   - Asosiy (Super) Admin yangi admin IDlarini qo'shishi yoki o'chirishi mumkin.

7. **⚙️ Sozlamalar**:
   - Start xabarini va Obuna matnini o'zgartirish.

---

## 🛠 O'rnatish va Ishga tushirish

### 1. Talablar:
- Python 3.10+ (tavsiya etiladi Python 3.12)

### 2. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 3. `.env` faylini sozlash:
`c:\Users\Lenovo\Desktop\qaaweee\.env` faylini oching va ma'lumotlarni kiriting:
```env
BOT_TOKEN=8078750038:AAELNO8PuGMpeMGE5YLhsOT-MNccA7_bJB8
SUPER_ADMIN_ID=7614962801
DB_PATH=anime_bot.db
```

### 4. Botni ishga tushirish:
```bash
python main.py
```

---

## 📁 Loyiha tuzilmasi

```
qaaweee/
├── config.py             # Sozlamalar va muhit o'zgaruvchilari
├── database.py           # SQLite bazasi va barcha CRUD funksiyalar
├── middlewares.py        # Obunani tekshirish va foydalanuvchini ro'yxatga olish
├── main.py               # Botni ishga tushirish fayli
├── requirements.txt      # Kutubxonalar ro'yxati
├── .env                  # Maxfiy kalitlar va sozlamalar
├── .env.example          # Namuna sozlamalar fayli
├── README.md             # Qo'llanma fayli
├── keyboards/
│   ├── user_kb.py        # Foydalanuvchi klaviaturalari
│   └── admin_kb.py       # Admin klaviaturalari
├── handlers/
│   ├── start.py          # /start va deep-link interfeysi
│   ├── user.py           # Qidiruv, katalog, videolarni olish
│   ├── admin_main.py     # Admin panel va statistika
│   ├── admin_anime.py    # Anime boshqaruvi
│   ├── admin_episode.py  # Qismlar boshqaruvi
│   ├── admin_channel.py  # Majburiy obuna boshqaruvi
│   ├── admin_user.py     # Foydalanuvchilarni boshqarish va bloklash
│   └── admin_settings.py # Sozlamalar va Adminlar boshqaruvi
├── states/
│   └── states.py         # FSM bosqichlari (Forms)
└── utils/
    └── helpers.py        # Link va matn formatlovchi yordamchilar
```
