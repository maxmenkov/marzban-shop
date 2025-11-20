from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def get_xtr_pay_keyboard(price: int, callback: str | None = None) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("Pay {amount}⭐️").format(amount=price), pay=True)
    if callback:
        builder.button(
            text=_("⬅️ Назад"),
            callback_data=f"back_pay_{callback}",
        )
    builder.adjust(1)
    return builder.as_markup()