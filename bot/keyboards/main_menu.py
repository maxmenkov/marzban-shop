from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _

from utils import get_i18n_string
import glv

def get_main_menu_keyboard(trial_expired:bool, lang=None) -> ReplyKeyboardMarkup:
    
    kb = [
        [
            KeyboardButton(text=get_i18n_str("Join 🏄🏻‍♂️", lang)),
        ],
        [
            KeyboardButton(text=get_i18n_str("Support ❤️", lang))
        ]
    ]

    kb_raw = [
        KeyboardButton(text=get_i18n_str("Frequent questions ℹ️", lang)),
        KeyboardButton(text=get_i18n_str("Instructions 📚", lang)),
    ]

    if trial_expired:
        kb_raw.insert(0, KeyboardButton(text=get_i18n_str("My subscription 👤", lang)))
    
    kb.insert(1, kb_raw)
        
    if not trial_expired and glv.config['TEST_PERIOD']:
        kb.insert(0, [KeyboardButton(text=get_trial_text(lang)),])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)   

def get_i18n_str(text: str, lang = None):
    if lang is None:
        return _(text)
    return get_i18n_string(text, lang)


def get_trial_text(lang=None) -> str:
    days = glv.config['TEST_PERIOD_DAYS']
    if lang is None:
        return _("{days} days free 🆓").format(days=days)
    return get_i18n_string("{days} days free 🆓", lang).format(days=days)
