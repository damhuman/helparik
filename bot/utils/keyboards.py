from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from configuration import ua_config


class MainKeyboards:

    @staticmethod
    def menu_keyboard():
        result_kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=ua_config.get('main_menu', 'wallet')),
                    KeyboardButton(text=ua_config.get('main_menu', 'intmax_wallet')),
                ],
                [
                    KeyboardButton(text=ua_config.get('main_menu', 'contacts'))
                ]
            ],
            resize_keyboard=True,
        )
        return result_kb

    @staticmethod
    def contact_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=ua_config.get("contact", "add_contact"),
                        callback_data="add_contact",
                    )
                ]
            ]
        )

    @staticmethod
    def transfer_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=ua_config.get("interaction", "confirm_send"),
                        callback_data="confirm_send",
                    ),
                    InlineKeyboardButton(
                        text=ua_config.get("interaction", "decline_send"),
                        callback_data="decline_send",
                    )

                ]
            ]
        )
