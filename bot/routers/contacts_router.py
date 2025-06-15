from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from configuration import ua_config

from bot.utils.message_generator import generate_contacts
from bot.utils.keyboards import MainKeyboards
from database.connector import DbConnector

contact_router = Router()


class ContactStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_wallet = State()


@contact_router.message(F.text == ua_config.get("main_menu", "contacts"))
async def contact_text_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = await generate_contacts(message.from_user.id)
    await message.reply(text=text, reply_markup=MainKeyboards.contact_keyboard())


@contact_router.callback_query(F.data == "add_contact")
async def add_contact_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ContactStates.waiting_for_name)
    await callback.message.reply(ua_config.get("contact", "enter_name"))
    await callback.answer()


@contact_router.message(ContactStates.waiting_for_name)
async def process_contact_name(message: Message, state: FSMContext) -> None:
    await state.update_data(contact_name=message.text)
    await state.set_state(ContactStates.waiting_for_wallet)
    await message.reply(ua_config.get("contact", "enter_wallet"))


@contact_router.message(ContactStates.waiting_for_wallet)
async def process_contact_wallet(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    contact_name = data["contact_name"]
    wallet_address = message.text

    db = DbConnector()
    await db.add_contact(
        telegram_id=message.from_user.id,
        contact_name=contact_name,
        wallet_address=wallet_address,
    )

    await state.clear()
    text = await generate_contacts(message.from_user.id)
    await message.reply(text=text, reply_markup=MainKeyboards.contact_keyboard())
