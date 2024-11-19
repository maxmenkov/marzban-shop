from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import insert, select, update, delete

from db.models import YPayments, CPayments, VPNUsers
import glv

engine = create_async_engine(
    glv.config['DB_URL'],
    pool_pre_ping=True,         # Автоматическая проверка соединения перед использованием
    pool_recycle=28000          # Закрывает и восстанавливает соединение каждые 3600 секунд (1 час)
)

import aiohttp
import re
from transliterate import translit

# Функция для очистки и транслитерации имени
def clean_and_transliterate(name: str) -> str:
    # Транслитерируем имя в латиницу
    transliterated_name = translit(name, 'ru', reversed=True)  # Преобразуем из кириллицы в латиницу
    # Оставляем только буквы (a-z), цифры и подчеркивания
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '', transliterated_name)
    return cleaned_name

async def get_username_by_tg_id(tg_id: int) -> str:
    tg_bot_token = glv.config['BOT_TOKEN']
    url = f"https://api.telegram.org/bot{tg_bot_token}/getChat?chat_id={tg_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        user = data.get('result')
                        username = user.get('username')
                        first_name = user.get('first_name', '')

                        # Если есть username, используем его
                        if username:
                            result = f"{username}_{tg_id}"
                        # Если username нет, используем first_name после очистки
                        else:
                            cleaned_first_name = clean_and_transliterate(first_name)
                            result = f"{cleaned_first_name}_{tg_id}"

                        # Обрезаем строку до 32 символов, но сохраняем подчеркивание
                        if len(result) > 32:
                            # Проверяем, чтобы символ "_" остался между именем и tg_id
                            max_name_len = 32 - len(str(tg_id)) - 1  # Отнимаем место для tg_id и "_"
                            result = result[:max_name_len] + f"_{tg_id}"

                        return result
                else:
                    print(f"Error fetching user: {response.status}")
                    return f"user_{tg_id}"[:32]
    except aiohttp.ClientError as e:
        print(f"Network error occurred: {e}")
        return f"user_{tg_id}"[:32]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"user_{tg_id}"[:32]

async def create_vpn_profile(tg_id: int):
    async with engine.connect() as conn:
        sql_query = select(VPNUsers).where(VPNUsers.tg_id == tg_id)
        result: VPNUsers = (await conn.execute(sql_query)).fetchone()
        if result is not None:
            return
        tg_username = await get_username_by_tg_id(tg_id)
        sql_query = insert(VPNUsers).values(tg_id=tg_id, vpn_id=tg_username)
        await conn.execute(sql_query)
        await conn.commit()

async def get_marzban_profile_db(tg_id: int) -> VPNUsers:
    async with engine.connect() as conn:
        sql_query = select(VPNUsers).where(VPNUsers.tg_id == tg_id)
        result: VPNUsers = (await conn.execute(sql_query)).fetchone()
    return result

async def get_marzban_profile_by_vpn_id(vpn_id: str):
    async with engine.connect() as conn:
        sql_query = select(VPNUsers).where(VPNUsers.vpn_id == vpn_id)
        result: VPNUsers = (await conn.execute(sql_query)).fetchone()
    return result    

async def had_test_sub(tg_id: int) -> bool:
    async with engine.connect() as conn:
        sql_query = select(VPNUsers).where(VPNUsers.tg_id == tg_id)
        result: VPNUsers = (await conn.execute(sql_query)).fetchone()
    return result.test

async def update_test_subscription_state(tg_id):
    async with engine.connect() as conn:
        sql_q = update(VPNUsers).where(VPNUsers.tg_id == tg_id).values(test=True)
        await conn.execute(sql_q)
        await conn.commit()

async def add_yookassa_payment(tg_id: int, callback: str, chat_id: int, lang_code: str, payment_id) -> dict:
    async with engine.connect() as conn:
        sql_q = insert(YPayments).values(tg_id=tg_id, payment_id=payment_id, chat_id=chat_id, callback=callback, lang=lang_code)
        await conn.execute(sql_q)
        await conn.commit()

async def add_cryptomus_payment(tg_id: int, callback: str, chat_id: int, lang_code: str, data) -> dict:
    async with engine.connect() as conn:
        sql_q = insert(CPayments).values(tg_id=tg_id, payment_uuid=data['order_id'], order_id=data['order_id'], chat_id=chat_id, callback=callback, lang=lang_code)
        await conn.execute(sql_q)
        await conn.commit()

async def get_yookassa_payment(payment_id) -> YPayments:
    async with engine.connect() as conn:
        sql_q = select(YPayments).where(YPayments.payment_id == payment_id)
        payment: YPayments = (await conn.execute(sql_q)).fetchone()
    return payment

async def get_cryptomus_payment(order_id) -> CPayments:
    async with engine.connect() as conn:
        sql_q = select(CPayments).where(CPayments.order_id == order_id)
        payment: CPayments = (await conn.execute(sql_q)).fetchone()
    return payment

async def delete_payment(payment_id):
    async with engine.connect() as conn:
        sql_q = delete(YPayments).where(YPayments.payment_id == payment_id)
        await conn.execute(sql_q)
        await conn.commit()
        sql_q = delete(CPayments).where(CPayments.payment_uuid == payment_id)
        await conn.execute(sql_q)
        await conn.commit()
