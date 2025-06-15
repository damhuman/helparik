import logging
from typing import Optional, List

from sqlalchemy.future import select
from sqlalchemy import update, delete

from services.singleton import SingletonMeta
from database.base import get_session
from database.models.user import User, Contact

logger = logging.getLogger(__name__)


class DbConnector(metaclass=SingletonMeta):
    """
    Asynchronous Database abstraction
    """

    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        async with get_session() as session:
            result = await session.execute(
                select(User).filter(User.telegram_id == telegram_id)
            )
            user = result.scalars().first()
            if user is None:
                user = User(telegram_id=telegram_id, username=username)
                session.add(user)
                await session.flush()
            return user

    async def get_user(self, telegram_id: int) -> Optional[User]:
        async with get_session() as session:
            result = await session.execute(
                select(User).filter(User.telegram_id == telegram_id)
            )
            user = result.scalars().first()
            return user

    async def get_all_users(self) -> List[User]:
        async with get_session() as session:
            result = await session.execute(
                select(User)
            )
            users = result.scalars().all()
            return users
    
    async def update_user(self, user: User) -> bool:
        async with get_session() as session:
            stmt = (
                update(User)
                .where(User.telegram_id == user.telegram_id)
                .values(username=user.username)
            )
            await session.execute(stmt)
            return True

    async def set_wallet_details(self, user: User, wallet_address: str, keystore: dict) -> bool:
        async with get_session() as session:
            stmt = (
                update(User)
                .where(User.telegram_id == user.telegram_id)
                .values(wallet_address=wallet_address, keystore=keystore)
            )
            await session.execute(stmt)
            return True

    async def get_contacts(self, telegram_id: int) -> List[Contact]:
        async with get_session() as session:
            result = await session.execute(
                select(Contact)
                .where(Contact.telegram_id == telegram_id)
            )
            contacts = result.scalars().all()
            return contacts

    async def add_contact(self, telegram_id: int, contact_name: str, wallet_address: str) -> Contact:
        async with get_session() as session:
            contact = Contact(
                telegram_id=telegram_id,
                contact_name=contact_name,
                wallet_address=wallet_address
            )
            session.add(contact)
            await session.flush()
            return contact
