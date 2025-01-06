import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import callbacks
import handlers
from config import API_TOKEN

dp = Dispatcher()


async def main() -> None:
    dp.include_routers(handlers.router, callbacks.router)
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("бот остановлен")
