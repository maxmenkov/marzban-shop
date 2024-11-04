import asyncio
import time
import glv
import logging
from db.methods import get_marzban_profile_by_vpn_id
from utils import marzban_api, get_i18n_string
from aiogram.exceptions import TelegramBadRequest

expired_sent_users = set()

async def notify_users_about_expired_sub():
    logging.info("Starting user notifications for subscription expired.")
    marzban_users_to_notify = await get_marzban_users_to_notify()
    logging.info(f"Found users to notify: {len(marzban_users_to_notify) if marzban_users_to_notify else 0}")

    if not marzban_users_to_notify:
        return

    for marzban_user in marzban_users_to_notify:
        vpn_id = marzban_user['username']
        user = await get_marzban_profile_by_vpn_id(vpn_id)
        if user is None or user.tg_id in expired_sent_users:
            continue

        try:
            chat_member = await glv.bot.get_chat_member(user.tg_id, user.tg_id)
            if chat_member is None:
                continue

            message = get_i18n_string("message_notify_expired_sub", chat_member.user.language_code).format(name=chat_member.user.first_name)

            await glv.bot.send_message(user.tg_id, message)
            expired_sent_users.add(user.tg_id)
            logging.info(f"Notification sent to user {user.tg_id}.")

        except TelegramBadRequest as e:
            logging.error(f"Error sending message to {user.tg_id}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error for user {user.tg_id}: {str(e)}")

async def reset_expired_sent_users():
    while True:
        await asyncio.sleep(86400)  # 86400 seconds = 24 hours
        expired_sent_users.clear()

async def get_marzban_users_to_notify():
    res = await marzban_api.panel.get_users()
    if res is None:
        return []
    users = res['users']
    return list(filter(filter_users_to_notify, users))

def filter_users_to_notify(user):
    user_expire_date = user['expire']
    if user_expire_date is None:
        return False

    now = int(time.time())
    yestarday = now - 60 * 60 * 24

    return yestarday < user_expire_date < now
