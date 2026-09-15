import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ⚠️ ВСТАВЬ СВОЙ КЛЮЧ БОТА МЕЖДУ КАВЫЧКАМИ:
BOT_TOKEN = "8619618419:AAFfKjA5UWOAxOekoflSmW2hGg05N5y3U-w"

# Твоя готовая рабочая ссылка на тапалку:
WEBAPP_URL = "https://github.io"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    # Создаем кнопку-ссылку, которая открывает WebApp внутри Telegram
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Запустить AlphaX Coin", 
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ])
    
    await message.answer(
        f"Привет! 🦾\n\n"
        f"Добро пожаловать в официальное приложение **AlphaX Coin**.\n"
        f"Копи очки AXP, прокачивай сеть и готовься к распределению токенов!\n\n"
        f"Нажми кнопку ниже, чтобы начать играть:",
        reply_markup=kb
    )

async def main():
    print("Бот AlphaX успешно запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
