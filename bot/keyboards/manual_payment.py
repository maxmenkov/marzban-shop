from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

import glv


def get_manual_payment_keyboard(payment_id: int, callback: str | None = None) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    if glv.config.get('PAY_SBER_URL'):
        builder.button(
            text=_('Sber'),
            url=glv.config['PAY_SBER_URL']
        )

    if glv.config.get('PAY_TBANK_URL'):
        builder.button(
            text=_('T-Bank'),
            url=glv.config['PAY_TBANK_URL']
        )

    builder.button(
        text=_('I have paid ✅'),
        callback_data=f"manual_paid_{payment_id}"
    )

    if callback:
        builder.button(
            text=_('⬅️ Назад'),
            callback_data=f"back_manual_{payment_id}",
        )

    builder.adjust(2, 1, 1)
    return builder.as_markup()


def get_manual_admin_keyboard(payment_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_('Confirm ✅'),
        callback_data=f"manual_confirm_{payment_id}"
    )
    builder.button(
        text=_('Reject ❌'),
        callback_data=f"manual_reject_{payment_id}"
    )
    builder.adjust(2)
    return builder.as_markup()
