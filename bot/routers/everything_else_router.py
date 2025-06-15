from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.utils.ai_helper import transcribe_audio, understand_action
from database.connector import DbConnector
from configuration import ua_config

from bot.utils.eth_accounts import WalletManager
from bot.utils.message_generator import generate_initial_message
from bot.utils.keyboards import MainKeyboards
from bot.utils.eth_connector import ETHConnector

everything_else_router = Router()


class EverythingElseStates(StatesGroup):
    wait_for_user_decision = State()
    understood_user_decision = State()


@everything_else_router.message(F.voice)
async def voice_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    file = await message.bot.download(message.voice.file_id)
    transcribed_text = await transcribe_audio(file, message.chat.id)
    action, contact, amount, network, status = await understand_action(transcribed_text, message.chat.id)

    await state.set_data(
        {
            "action": action,
            "contact": contact,
            "amount": amount,
            "network": network,
        }
    )

    await message.reply(
        text=f"Do you want {action} {amount} to {contact} on {network} network?",
        reply_markup=MainKeyboards.transfer_keyboard(),
    )

@everything_else_router.callback_query(F.data == "confirm_send")
async def confirmed_transfer_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    # send it
    await callback.message.reply(text=ua_config.get("interaction", "transfer_confirmed").format(**data))
    await callback.answer()


@everything_else_router.callback_query(F.data == "decline_send")
async def declined_transfer_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.reply(text=ua_config.get("interaction", "transfer_declined"))
    await callback.answer()


@everything_else_router.message()
async def everything_else_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = message.text.split(" ")
    address = text[0]
    amount = 0.005
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=message.from_user.id)
    private_key = WalletManager.load_private_key(user.keystore)
    eth_con = ETHConnector(private_key_hex=private_key)
    await eth_con.send_native(to_address=address, amount=amount)
    await message.reply("done")
