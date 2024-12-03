import ipaddress

from aiohttp.web_request import Request
from aiohttp import web

from db.methods import (
    get_marzban_profile_db,
    get_payment,
    delete_payment,
    confirm_payment,
    PaymentPlatform
)
from keyboards import get_main_menu_keyboard
from utils import webhook_data, goods, marzban_api
from utils import get_i18n_string
import glv

YOOKASSA_IPS = (
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11",
    "77.75.156.35",
    "77.75.154.128/25",
    "2a02:5180::/32"
)

async def check_crypto_payment(request: Request):
    client_ip = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For') or request.remote
    if client_ip not in ["91.227.144.54"]:
        return web.Response(status=403)
    data = await request.json()
    if not webhook_data.check(data, glv.config['CRYPTO_TOKEN']):
        return web.Response(status=403)
    payment = await get_payment(data['order_id'], PaymentPlatform.cryptomus)
    if payment == None:
        return web.Response()
    if data['status'] in ['paid', 'paid_over']:
        good = goods.get(payment.callback)
        user = await get_marzban_profile_db(payment.tg_id)
        await marzban_api.generate_marzban_subscription(user.vpn_id, good)
        text = get_i18n_string("Thank you for choice ❤️\n️\n<a href=\"{link}\">Subscribe</a> so you don't miss any announcements ✅\n️\nYour subscription is purchased and available in the \"Access to VPN 🏄🏻‍♂️\" section.", payment.lang)
        await glv.bot.send_message(payment.tg_id,
            text.format(
                link=glv.config['TG_INFO_CHANEL']
            ),
            reply_markup=get_main_menu_keyboard(True, payment.lang)
        )
        await confirm_payment(payment.payment_id)
    if data['status'] == 'cancel':
        await delete_payment(payment.payment_id)
    return web.Response()

async def check_yookassa_payment(request: Request):
    client_ip = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For') or request.remote
    f = True
    for subnet in YOOKASSA_IPS:
        if "/" in subnet:
            if ipaddress.ip_address(client_ip) in ipaddress.ip_network(subnet):
                f = False
                break
        else:
            if client_ip == subnet:
                f = False
                break
    if f:
        return web.Response(status=403)
    data = (await request.json())['object']
    payment = await get_payment(data['id'], PaymentPlatform.yookassa)
    if payment == None:
        return web.Response()
    if data['status'] in ['succeeded']:
        good = goods.get(payment.callback)
        user = await get_marzban_profile_db(payment.tg_id)
        await marzban_api.generate_marzban_subscription(user.vpn_id, good)
        text = get_i18n_string("Thank you for choice ❤️\n️\n<a href=\"{link}\">Subscribe</a> so you don't miss any announcements ✅\n️\nYour subscription is purchased and available in the \"Access to VPN 🏄🏻‍♂️\" section.", payment.lang)
        await glv.bot.send_message(payment.tg_id,
            text.format(
                link=glv.config['TG_INFO_CHANEL']
            ),
            reply_markup=get_main_menu_keyboard(True, payment.lang)
        )
        await confirm_payment(payment.payment_id)
    if data['status'] == 'canceled':
        await delete_payment(payment.payment_id)
    return web.Response()
