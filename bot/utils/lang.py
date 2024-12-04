import gettext 
from pathlib import Path

import logging 

_ = gettext.gettext

domain = 'bot'
localedir = 'locales'

def get_i18n_string(s, lang) -> str:
    logging.info("lang: " + lang)
    if lang in ['ru']:
        logging.info("Getting translations from: " + str(Path(__file__).parent.parent / localedir))
        language_translations = gettext.translation(domain, Path(__file__).parent.parent / localedir, languages=[lang])
        language_translations.install()
        logging.info(_(s))
        return _(s)
    logging.info("Getting default translations from: localedir")
    language_translations = gettext.translation(domain, localedir, languages=['en'])
    language_translations.install()
    
    return _(s)