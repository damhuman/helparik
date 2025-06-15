from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database.connector import DbConnector
from configuration import ua_config

from bot.utils.eth_accounts import WalletManager
from bot.utils.message_generator import generate_initial_message
from bot.utils.keyboards import MainKeyboards

registration_router = Router()


@registration_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    db_connector = DbConnector()
    user = await db_connector.get_user(message.from_user.id)
    if user.wallet_address is None:
        wallet = WalletManager.create_wallet()
        await db_connector.set_wallet_details(
            user, wallet["address"], wallet["keystore"]
        )
    text = await generate_initial_message(message.from_user.id)
    await message.reply(text=text, reply_markup=MainKeyboards.menu_keyboard())
