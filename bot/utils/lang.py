import gettext 
from pathlib import Path

domain = 'bot'
localedir = 'locales'

def get_i18n_string(s, lang) -> str:
    if lang in ['ru']:
        language_translations = gettext.translation(domain, Path(__file__).parent.parent / localedir, languages=[lang])
        language_translations.install()
        
        return gettext.gettext(s)
    language_translations = gettext.translation(domain, localedir, languages=['en'])
    language_translations.install()
    
    return gettext.gettext(s)