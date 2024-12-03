from aiogram import Router, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _

from utils import goods, marzban_api
from db.methods import get_marzban_profile_db
from keyboards import get_main_menu_keyboard

import glv

router = Router(name="payment-router")

@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    if goods.get(query.invoice_payload) is None:
        return await query.answer(_("Error: Invalid product type.\nPlease contact the support team."), ok = False)
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def success_payment(message: Message):
    good = goods.get(message.successful_payment.invoice_payload)
    user = await get_marzban_profile_db(message.from_user.id)
    await marzban_api.generate_marzban_subscription(user.vpn_id, good)
    await message.answer(
        text = _("Thank you for choice ❤️\n️\n<a href=\"{link}\">Subscribe</a> so you don't miss any announcements ✅\n️\nYour subscription is purchased and available in the \"Access to VPN 🏄🏻‍♂️\" section.").format(
            link=glv.config['TG_INFO_CHANEL']),
        reply_markup=get_main_menu_keyboard(True, message.from_user.language_code))
    
def register_payments(dp: Dispatcher):
    dp.include_router(router)