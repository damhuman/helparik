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
    transaction_confirmation = State()


@everything_else_router.message(F.voice)
async def voice_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    file = await message.bot.download(message.voice.file_id)
    transcribed_text = await transcribe_audio(file, message.chat.id)
    action, username, address, amount, network = await understand_action(transcribed_text, message.chat.id)
    if action == "ERROR":
        await message.reply(
            ua_config.get('main', 'invalid_action')
        )
        return
    if username == "ERROR" or address == "ERROR":
        await message.reply(
            ua_config.get('main', 'invalid_receiver')
        )
        return
    if amount == "ERROR":
        await message.reply(
            ua_config.get('main', 'invalid_amount')
        )

    if action == 'TRANSFER':
        await state.set_state(EverythingElseStates.transaction_confirmation)
        await state.update_data(amount=amount, address=address)
        await message.reply(
            ua_config.get('transactions', 'transfer').format(
                amount=amount,
                address=f'{address} ({username})'
            ),
            reply_markup=MainKeyboards.yes_no_keyboard()
        )
        return

    await message.reply(
        text=ua_config.get('main', 'error_processing_request')
    )


@everything_else_router.callback_query()
async def transaction_confirmation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'no':
        await state.clear()
        await callback.message.bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text=ua_config.get('transactions', 'no_confirmation')
        )
        return
    data = await state.get_data()
    amount = float(data.get('amount').split(' ')[0])
    address = data.get('address')
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=callback.message.chat.id)
    private_key = WalletManager.load_private_key(user.keystore)
    eth_con = ETHConnector(private_key_hex=private_key)
    try:
        res = await eth_con.send_native(to_address=address, amount=amount)
    except Exception as e:
        await state.clear()
        await callback.message.bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text=ua_config.get('transactions', 'problems_with_transactions').format(error=e)
        )
        return
    await state.clear()
    await callback.message.bot.edit_message_text(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        text=ua_config.get('transactions', 'success_transaction').format(txid=res),
        reply_markup=MainKeyboards.blockchain_explorer_button(txid=res)
    )


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
