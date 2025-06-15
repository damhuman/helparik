from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.utils.ai_helper import transcribe_audio
from database.connector import DbConnector
from configuration import ua_config

from bot.utils.eth_accounts import WalletManager
from bot.utils.message_generator import generate_initial_message
from bot.utils.keyboards import MainKeyboards
from bot.utils.eth_connector import ETHConnector

everything_else_router = Router()


@everything_else_router.message(F.voice)
async def voice_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    byte_file = BytesIO()
    await message.bot.download(message.voice.file_id, byte_file)
    byte_file.seek(0)
    byte_file.name = 'voice.ogg'
    # byte_file.t
    text = await transcribe_audio(byte_file)
    await message.reply(text=text,)

@everything_else_router.message()
async def everything_else_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = message.text.split(' ')
    address = text[0]
    amount = 0.005
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=message.from_user.id)
    private_key = WalletManager.load_private_key(user.keystore)
    eth_con = ETHConnector(private_key_hex=private_key)
    await eth_con.send_native(to_address=address, amount=amount)
    await message.reply('done')


