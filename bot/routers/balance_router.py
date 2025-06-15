from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database.connector import DbConnector
from configuration import ua_config

from bot.utils.eth_accounts import WalletManager
from bot.utils.message_generator import generate_initial_message

balance_router = Router()


@balance_router.message(F.text == ua_config.get("main_menu", "wallet"))
async def wallet_text_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = await generate_initial_message(message.from_user.id)
    await message.reply(text=text)
