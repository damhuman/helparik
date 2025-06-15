from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from configuration import ua_config

from bot.utils.message_generator import generate_intmax_balance_message

intmax_balance_router = Router()


@intmax_balance_router.message(F.text == ua_config.get('main_menu', 'intmax_wallet'))
async def wallet_text_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = await generate_intmax_balance_message(message.from_user.id)
    await message.reply(text=text)
