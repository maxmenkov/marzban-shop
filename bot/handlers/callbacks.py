from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, LabeledPrice
from aiogram.utils.i18n import gettext as _

from keyboards import get_main_menu_keyboard, get_payment_keyboard, get_pay_keyboard, \
    get_buy_menu_keyboard, get_xtr_pay_keyboard, get_back_to_help_keyboard, get_help_keyboard, \
    get_months_keyboard, get_support_keyboard, get_reach_support_keyboard
from db.methods import is_trial_available, disable_trial_availability, get_marzban_profile_db

from utils import goods, yookassa, cryptomus, marzban_api
import glv

router = Router(name="callbacks-router") 

@router.callback_query(F.data.startswith("months_"))
async def callback_month_amount_select(callback: CallbackQuery):
    await callback.message.delete()
    months = callback.data.replace("months_", "")
    await callback.message.answer(text=_("Select the appropriate amount of traffic ⬇️"), reply_markup=get_buy_menu_keyboard(months))
    await callback.answer()

@router.callback_query(F.data.startswith("pay_kassa_"))
async def callback_payment_method_select(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.replace("pay_kassa_", "")
    if data not in goods.get_callbacks():
        await callback.answer()
        return
    result = await yookassa.create_payment(
        callback.from_user.id, 
        data, 
        callback.from_user.language_code)
    await callback.message.answer(
        _("To be paid – {amount} ₽ ⬇️").format(
            amount=int(result['amount'])
        ),
        reply_markup=get_pay_keyboard(result['url']))
    await callback.answer()


@router.callback_query(F.data.startswith("pay_stars_"))
async def callback_payment_method_select(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.replace("pay_stars_", "")
    if data not in goods.get_callbacks():
        await callback.answer()
        return
    good = goods.get(data)
    price = good['price']['stars']
    months = good['months']
    prices = [LabeledPrice(label="XTR", amount=price)]  
    await callback.message.answer_invoice(
        title= _("Subscription for {amount} month").format(amount=months),
        currency="XTR",
        description=_("To be paid - {amount} ⭐️ ⬇️").format(
            amount=int(price)
        ),
        prices=prices,
        provider_token="",
        payload=data,
        reply_markup=get_xtr_pay_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_crypto_"))
async def callback_payment_method_select(callback: CallbackQuery):
    await callback.message.delete()
    data = callback.data.replace("pay_crypto_", "")
    if data not in goods.get_callbacks():
        await callback.answer()
        return
    result = await cryptomus.create_payment(
        callback.from_user.id, 
        data,
        callback.from_user.language_code)
    now = datetime.now()
    expire_date = (now + timedelta(minutes=60)).strftime("%d/%m/%Y, %H:%M")
    await callback.message.answer(
        _("To be paid – {amount} $ ⬇️").format(
            amount=result['amount'],
            date=expire_date
        ),
        reply_markup=get_pay_keyboard(result['url']))
    await callback.answer()

@router.callback_query(F.data == ("trial"))
async def callback_trial(callback: CallbackQuery):
    await callback.message.delete()
    result = await is_trial_available(callback.from_user.id)
    if not result:
        await callback.message.answer(
            _("Your subscription is available in the \"Access to VPN 🏄🏼‍♂️\" section."),
            reply_markup=get_main_menu_keyboard())
        return
    result = await get_marzban_profile_db(callback.from_user.id)
    result = await marzban_api.generate_test_subscription(result.vpn_id)
    await disable_trial_availability(callback.from_user.id)
    await callback.message.answer(
        _("Thank you for choice ❤️\n️\n<a href=\"{link}\">Subscribe</a> so you don't miss any announcements ✅\n️\nYour subscription is purchased and available in the \"Access to VPN 🏄🏻‍♂️\" section.").format(
            link=glv.config['TG_INFO_CHANEL']),
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == ("payment"))
async def callback_payment(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(_("Select payment period ⬇️"), reply_markup=get_months_keyboard())

@router.callback_query(F.data == ("faq"))
async def callback_frequent_questions(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(_("message_frequent_questions").format(shop_name=glv.config['SHOP_NAME']), reply_markup=get_back_to_help_keyboard())

@router.callback_query(F.data == ("tos"))
async def callback_terms_of_service(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=_("message_terms_of_service"), reply_markup=get_back_to_help_keyboard())

@router.callback_query(F.data == ("help"))
async def callback_help(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=_("Select the action ⬇️"), reply_markup=get_help_keyboard())

@router.callback_query(F.data == ("support"))
async def callback_terms_of_service(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=_("What issue did you encounter?"), reply_markup=get_support_keyboard())

@router.callback_query(F.data == ("set_up_problem"))
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=_("message_set_up_vpn"), reply_markup=get_reach_support_keyboard())

@router.callback_query(F.data == ("working_problem"))
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=_("message_working_problem"), reply_markup=get_reach_support_keyboard())

@router.callback_query(lambda c: c.data in goods.get_callbacks())
async def callback_payment_method_select(callback: CallbackQuery):
    await callback.message.delete()
    good = goods.get(callback.data)
    await callback.message.answer(text=_("Select payment method ⬇️"), reply_markup=get_payment_keyboard(good))
    await callback.answer()

def register_callbacks(dp: Dispatcher):
    dp.include_router(router)
