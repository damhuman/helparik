from aiogram import Router

from bot.routers.registration_router import registration_router
from bot.routers.balance_router import balance_router
from bot.routers.intmax_wallet import intmax_balance_router
from bot.routers.contacts_router import contact_router
from bot.routers.everything_else_router import everything_else_router


main_router = Router()
main_router.include_router(registration_router)
main_router.include_router(balance_router)
main_router.include_router(intmax_balance_router)
main_router.include_router(contact_router)
main_router.include_router(everything_else_router)
