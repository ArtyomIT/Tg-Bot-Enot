import asyncio
import logging
from aiogram import Bot

from handlers import dp
from database import create_table

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Записываем токен от BotFather
API_TOKEN = '6886971807:AAH-cyGf3xQeSgc5vHu-2EK2oX-4SOF5QkU'

# Объект бота
bot = Bot(token=API_TOKEN)


# Запуск процесса поллинга новых апдейтов
async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
