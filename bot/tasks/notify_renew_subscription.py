import asyncio
import time
import glv
import logging
from db.methods import get_marzban_profile_by_vpn_id
from utils import marzban_api, get_i18n_string
from aiogram.exceptions import TelegramBadRequest

renew_sent_users = set()

async def notify_users_to_renew_sub():
    logging.info("Starting user notifications for subscription renewal.")
    marzban_users_to_notify = await get_marzban_users_to_notify()
    logging.info(f"Found users to notify: {len(marzban_users_to_notify) if marzban_users_to_notify else 0}")

    if not marzban_users_to_notify:
        return

    success_count = 0  # Переменная для подсчета успешных отправок
    
    for idx, marzban_user in enumerate(marzban_users_to_notify):
        vpn_id = marzban_user['username']
        user = await get_marzban_profile_by_vpn_id(vpn_id)
        if user is None:
            logging.info(f"User {vpn_id} not found in profile database.")
            continue
        if user.tg_id in renew_sent_users:
            logging.info(f"User {user.tg_id} already received renewal notification last 24 h. Skipping.")
            continue
        # Устанавливаем язык пользователя по-умолчанию
        language_code = 'ru'
        try:
            # Получаем язык пользователя через Telegram API
            chat_member = await glv.bot.get_chat_member(user.tg_id, user.tg_id)
            language_code = chat_member.user.language_code if hasattr(chat_member.user, 'language_code') else 'ru'

            # Формируем сообщение на основе языка
            message = get_i18n_string("Hello, {name} 👋🏻\n\nThank you for using our service ❤️\n️\nYour VPN subscription expires {day}, at the end of the day.\n️\nTo renew it, just go to the \"Join 🏄🏻‍♂️\" section and make a payment.", chat_member.user.language_code).format(
                name=chat_member.user.first_name,
                day=get_expiration_day_str(marzban_user, chat_member.user.language_code))
           # Отправляем сообщение
            await glv.bot.send_message(user.tg_id, message)
            renew_sent_users.add(user.tg_id)
            success_count += 1  # Увеличиваем счетчик успешных отправок
            logging.info(f"Notification sent to user {user.tg_id}. Successful sends: {success_count}")

            # Задержка в 1 секунду после успешной отправки сообщения
            await asyncio.sleep(1)

            # Задержка каждые 50 сообщений на 15 секунд
            if (idx + 1) % 50 == 0:
                logging.info("Pausing for 15 seconds to prevent rate limit issues...")
                await asyncio.sleep(15)

        except TelegramBadRequest as e:
            if "too many requests" in str(e).lower():
                logging.error(f"Rate limit exceeded for user {user.tg_id}. Retrying after 15 seconds.")
                await asyncio.sleep(15)  # Ожидание перед повторной попыткой
                try:
                    await glv.bot.send_message(user.tg_id, message)
                    expired_sent_users.add(user.tg_id)
                    success_count += 1
                    logging.info(f"Notification successfully resent to user {user.tg_id} after rate limit delay.")
                except TelegramBadRequest as retry_e:
                    logging.error(f"Retry failed for user {user.tg_id}: {str(retry_e)}")
                    if "chat not found" in str(retry_e).lower():
                        logging.error(f"User {user.tg_id} has blocked the bot or is not reachable.")
                    await asyncio.sleep(1)  # Задержка после повторной ошибки
            elif "chat not found" in str(e).lower():
                logging.error(f"User {user.tg_id} has blocked the bot or is not reachable.")
                await asyncio.sleep(1)  # Задержка после ошибки
            else:
                # Прочие ошибки от Telegram API
                logging.error(f"TelegramBadRequest error for user {user.tg_id}: {str(e)}")
                await asyncio.sleep(1)  # Задержка после ошибки
        except Exception as e:
            logging.error(f"Unexpected error for user {user.tg_id}: {str(e)}")
            await asyncio.sleep(1)  # Задержка после ошибки

    logging.info(f"Total successful notifications sent: {success_count}")

async def reset_renew_sent_users():
    while True:
        await asyncio.sleep(82800)  # 86400 seconds = 24 hours
        renew_sent_users.clear()
        logging.info("Renew sent users list has been cleared.")

async def get_marzban_users_to_notify():
    res = await marzban_api.panel.get_users()
    if res is None:
        return []
    users = res['users']
    logging.info(f"Found {len(users)} users in base.")
    users_to_notify = [user for user in users if user['status'] != 'disabled']
    logging.info(f"Found {len(users_to_notify)} users to notify after filtering disabled users.")
    return list(filter(filter_users_to_notify, users_to_notify))

def filter_users_to_notify(user):
    user_expire_date = user['expire']
    if user_expire_date is None:
        logging.info(f"User {user['username']} skipped due to missing expiration date.")
        return False
    now = int(time.time())
    after_tomorrow = now + 60 * 60 * 36
    return now < user_expire_date < after_tomorrow

def get_expiration_day_str(user, lang):
    if user['expire'] < int(time.time()) + 60 * 60 * 12:
        return get_i18n_string("today", lang)
    return get_i18n_string("tomorrow", lang)
