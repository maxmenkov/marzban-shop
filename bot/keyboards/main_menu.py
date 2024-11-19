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
            KeyboardButton(text=get_i18n_str("Frequent questions ℹ️", lang))
    ]

    kb_raw.insert(0, KeyboardButton(text=get_i18n_str("My subscription 👤", lang)))
    
    kb.insert(1, kb_raw)
        
    if not trial_expired and glv.config['TEST_PERIOD']:
        kb.insert(0, [KeyboardButton(text=get_i18n_str("5 days free 🆓", lang)),])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)   

def get_i18n_str(text: str, lang = None):
    if lang is None:
        return _(text)
    return get_i18n_string(text, lang)
