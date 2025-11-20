from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def get_instructions_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="iOS", callback_data="instr_ios"))
    builder.row(InlineKeyboardButton(text="macOS", callback_data="instr_macos"))
    builder.row(InlineKeyboardButton(text="Android", callback_data="instr_android"))
    builder.row(InlineKeyboardButton(text="Windows", callback_data="instr_windows"))
    builder.row(InlineKeyboardButton(text="Linux", callback_data="instr_linux"))
    builder.row(
        InlineKeyboardButton(
            text=_("⬅️ Назад"),
            callback_data="back:main",
        )
    )
    return builder.as_markup()
