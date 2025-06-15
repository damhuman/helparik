from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from database.connector import DbConnector

from configuration import ua_config


class UserToContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        db_con = DbConnector()
        user = data['event_from_user']
        data['user'] = await db_con.get_or_create_user(user.id, user.username)
        process = False
        if event.chat.type == 'private':
            process = True
        if event.chat.join_by_request:
            process = True
        if process:
            return await handler(event, data)


class UpdateUsernameMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = data['user']
        from_user = data['event_from_user']
        if user.username != from_user.username:
            user.username = from_user.username
            await DbConnector().update_user(user)
        return await handler(event, data)
