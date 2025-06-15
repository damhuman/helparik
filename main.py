import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from bot.middleware.user_base import UserToContextMiddleware, UpdateUsernameMiddleware
from configuration import BOT_TOKEN
from bot.routers.main_router import main_router
from bot.services.redis_client import redis_client


async def main() -> None:
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)

    # Register middlewares
    dp.message.middleware(UserToContextMiddleware())
    dp.message.middleware(UpdateUsernameMiddleware())

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
