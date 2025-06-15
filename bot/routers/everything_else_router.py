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
from bot.utils.intmax_connector import IntMaxConnector

everything_else_router = Router()


class EverythingElseStates(StatesGroup):
    transaction_confirmation = State()
    deposit_confirmation = State()
    withdraw_confirmation = State()


async def make_deposit(amount: float, telegram_id: int):
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=telegram_id)
    private_key = WalletManager.load_private_key(user.keystore)
    async with IntMaxConnector() as connector:
        await connector.login(f'0x{private_key}')
        res = await connector.deposit(amount=amount, 
            token={
                "tokenIndex": 0,
                "symbol": 'ETH',
                "decimals": 18,
                "contractAddress": '0x0000000000000000000000000000000000000000',
                "createdAt": { "_seconds": 1748082445, "_nanoseconds": 385000000 },
                "tokenType": 0
            }
        )
    return res['result']['status'], res['result']['txHash']


async def make_withdraw(amount: float, telegram_id: int):
    db_con = DbConnector()
    print('hey1')
    user = await db_con.get_user(telegram_id=telegram_id)
    private_key = WalletManager.load_private_key(user.keystore)
    async with IntMaxConnector() as connector:
        await connector.login(f'0x{private_key}')
        print('hey')
        res = await connector.withdraw(amount=amount,
            token={
                "tokenIndex": 0,
                "symbol": 'ETH',
                "decimals": 18,
                "contractAddress": '0x0000000000000000000000000000000000000000',
                "createdAt": { "_seconds": 1748082445, "_nanoseconds": 385000000 },
                "tokenType": 0
            },
            address=user.wallet_address
        )
    return res['tx']['txTreeRoot']


async def make_withdraw(amount: float, telegram_id: int):
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=telegram_id)
    private_key = WalletManager.load_private_key(user.keystore)
    async with IntMaxConnector() as connector:
        await connector.login(f'0x{private_key}')
        res = await connector.withdraw(amount=amount,
            token={
                "tokenIndex": 0,
                "symbol": 'ETH',
                "decimals": 18,
                "contractAddress": '0x0000000000000000000000000000000000000000',
                "createdAt": { "_seconds": 1748082445, "_nanoseconds": 385000000 },
                "tokenType": 0
            },
            address=user.wallet_address
        )
    return res['tx']['txTreeRoot']


async def make_transfer(amount: float, telegram_id: int, address: str):
    db_con = DbConnector()
    user = await db_con.get_user(telegram_id=telegram_id)
    private_key = WalletManager.load_private_key(user.keystore)
    transfers = [{
        'address': address,
        'amount': amount,
        'token': {
            "tokenIndex": 0,
            "symbol": 'ETH',
            "decimals": 18,
            "contractAddress": '0x0000000000000000000000000000000000000000',
            "createdAt": { "_seconds": 1748082445, "_nanoseconds": 385000000 },
            "tokenType": 0
        }
    }]
    async with IntMaxConnector() as connector:
        await connector.login(f'0x{private_key}')
        res = await connector.broadcast_transaction(transfers=transfers)
    return res['tx']['txTreeRoot']


@everything_else_router.message(F.voice)
async def voice_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    file = await message.bot.download(message.voice.file_id)
    transcribed_text = await transcribe_audio(file, message.chat.id)
    action, username, address, amount, network = await understand_action(transcribed_text, message.chat.id)
    if amount == "ERROR":
        await message.reply(
            ua_config.get('main', 'invalid_amount')
        )
        return
    
    if action == "DEPOSIT":
        await state.set_state(EverythingElseStates.deposit_confirmation)
        if 'eth' not in amount.lower():
            amount += ' ETH'
        await state.update_data(amount=amount)
        await state.update_data(network=network)
        await message.reply(
            text=ua_config.get('transactions', 'deposit_confirm').format(amount=amount),
            reply_markup=MainKeyboards.yes_no_keyboard()
        )
        return

    if action == "WITHDRAW":
        await state.set_state(EverythingElseStates.withdraw_confirmation)
        if 'eth' not in amount.lower():
            amount += ' ETH'
        await state.update_data(amount=amount)
        await state.update_data(network=network)
        await message.reply(
            text=ua_config.get('transactions', 'withdraw_confirm').format(amount=amount),
            reply_markup=MainKeyboards.yes_no_keyboard()
        )
        return

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

    if action == 'TRANSFER':
        await state.set_state(EverythingElseStates.transaction_confirmation)
        await state.update_data(amount=amount, address=address, network=network)
        await message.reply(
            ua_config.get('transactions', 'transfer').format(
                amount=amount,
                address=f'{address} ({username})',
                network=network
            ),
            reply_markup=MainKeyboards.yes_no_keyboard()
        )
        return

    await message.reply(
        text=ua_config.get('main', 'invalid_action')
    )


@everything_else_router.callback_query(EverythingElseStates.transaction_confirmation)
async def transaction_confirmation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'no':
        await state.clear()
        await callback.message.bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text=ua_config.get('transactions', 'no_confirmation')
        )
        return
    await callback.message.bot.edit_message_text(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        text=ua_config.get('main', 'processing')
    )
    data = await state.get_data()
    amount = float(data.get('amount').split(' ')[0])
    network = data.get('network')
    address = data.get('address')
    if network.lower() == 'intmax':
        try:
            txid = await make_transfer(amount, callback.message.chat.id, address=address)
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
            text=ua_config.get('transactions', 'success_transaction_intmax').format(txid=txid),
            reply_markup=MainKeyboards.blockchain_explorer_button(txid=txid)
        )

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
        reply_markup=MainKeyboards.blockchain_explorer_button(txid=f'0x{res}')
    )


@everything_else_router.callback_query(EverythingElseStates.deposit_confirmation)
async def deposit_confirmation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'no':
        await state.clear()
        await callback.message.bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text=ua_config.get('transactions', 'no_confirmation')
        )
        return
    await callback.message.bot.edit_message_text(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        text=ua_config.get('main', 'processing')
    )
    data = await state.get_data()
    amount = float(data.get('amount').split(' ')[0])
    try:
        status, txid = await make_deposit(amount=amount, telegram_id=callback.message.chat.id)
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
        text=ua_config.get('transactions', 'success_deposit').format(txid=txid),
        reply_markup=MainKeyboards.blockchain_explorer_button(txid=txid)
    )


@everything_else_router.callback_query(EverythingElseStates.withdraw_confirmation)
async def withdraw_confirmation_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'no':
        await state.clear()
        await callback.message.bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text=ua_config.get('transactions', 'no_confirmation')
        )
        return
    await callback.message.bot.edit_message_text(
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        text=ua_config.get('main', 'processing')
    )
    data = await state.get_data()
    amount = float(data.get('amount').split(' ')[0])
    try:
        txid = await make_withdraw(amount=amount, telegram_id=callback.message.chat.id)
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
        text=ua_config.get('transactions', 'success_withdraw').format(txid=txid),
        reply_markup=MainKeyboards.blockchain_explorer_button(txid=txid)
    )


@everything_else_router.message()
async def everything_else_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    print('hey')
    await make_deposit(amount=0.0001, telegram_id=message.from_user.id)
