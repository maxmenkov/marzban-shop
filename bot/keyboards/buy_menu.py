from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from utils import goods

def get_buy_menu_keyboard(months) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    subscription_opts = goods.get()
    months = int(months)
    filtered_goods = list(filter(lambda good: good['months'] == months, subscription_opts))
    for good in filtered_goods:
        builder.row(InlineKeyboardButton(
            text=_("{title} — {price_ru}₽").format(
                title=good['title'],
                price_ru=good['price']['ru']
            ), 
            callback_data=good['callback'])
        )
    return builder.as_markup()
