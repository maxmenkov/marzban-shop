from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def get_pay_keyboard(pay_url: str, callback: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("Pay 💳"),
            url=pay_url,
        )
    )
    if callback:
        builder.row(
            InlineKeyboardButton(
                text=_("⬅️ Назад"),
                callback_data=f"back_pay_{callback}",
            )
        )
    return builder.as_markup()
