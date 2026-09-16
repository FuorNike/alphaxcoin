import asyncio
import json
import sqlite3
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# ⚠️ ТВОЙ ТОКЕН БОТА ОТ @BotFather:
BOT_TOKEN = "8619618419:AAFBN58siBcfTILxueN9YpbYZ4Aj0CD8C_4"
WEBAPP_URL = "https://fuornike.github.io/alphaxcoin/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БЛОК БАЗЫ ДАННЫХ (SQLite) ---
def init_db():
    conn = sqlite3.connect("users_score.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            score INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_score(user_id):
    conn = sqlite3.connect("users_score.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def save_score(user_id, score):
    conn = sqlite3.connect("users_score.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, score) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET score = excluded.score
    """, (user_id, score))
    conn.commit()
    conn.close()

# --- БЛОК TELEGRAM БОТА ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Запустить AlphaX Coin", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        "Привет! 🦾\n\nДобро пожаловать в синхронизированное приложение **AlphaX Coin**.\n"
        "Твой баланс теперь привязан к аккаунту и доступен с любого устройства!\n\n"
        "Нажми кнопку ниже, чтобы начать играть:", reply_markup=kb
    )

# --- БЛОК API СЕРВЕРА ДЛЯ СИНХРОНИЗАЦИИ ---
async def handle_get_score(request):
    user_id = request.match_info.get('user_id')
    if not user_id:
        return web.Response(status=400, text="Missing user_id", headers={"Access-Control-Allow-Origin": "*"})
    score = get_score(int(user_id))
    return web.json_response({"score": score}, headers={"Access-Control-Allow-Origin": "*"})

async def handle_save_score(request):
    try:
        data = await request.json()
        user_id = data.get('user_id')
        score = data.get('score')
        if user_id is None or score is None:
            return web.Response(status=400, text="Invalid data", headers={"Access-Control-Allow-Origin": "*"})
        save_score(int(user_id), int(score))
        return web.json_response({"status": "success"}, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return web.Response(status=500, text=str(e), headers={"Access-Control-Allow-Origin": "*"})

# 👑 ГЛАВНЫЙ ФИКС ДЛЯ РЕНДЕРА (Корневой адрес)
# Когда Render будет пинговать сервер, этот метод сразу вернет "OK", и плашка станет зеленой LIVE!
async def handle_index(request):
    return web.Response(text="AlphaX Server Active 🚀", headers={"Access-Control-Allow-Origin": "*"})

async def handle_options(request):
    return web.Response(headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    })

async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def main():
    init_db()
    
    app = web.Application()
    # Привязываем обработчики к путям
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/score/{user_id}', handle_get_score)
    app.router.add_post('/api/score', handle_save_score)
    
    # CORS префлайты
    app.router.add_options('/api/score', handle_options)
    app.router.add_options('/api/score/{user_id}', handle_options)
    
    # Render автоматически передает нужный ему порт в переменные среды PORT. Если ее нет — берем 10000
    port = int(os.environ.get("PORT", 10000))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    await asyncio.gather(
        site.start(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())
