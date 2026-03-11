"""
DM SENTINEL - Internationalization (i18n) System
=================================================
Multi-language support for security reports and UI
Supported languages: Spanish, English, French, Portuguese, Esperanto
"""

import json
import os
from typing import Dict, Any, Optional


class I18nManager:
    """Manage translations for multiple languages"""
    
    SUPPORTED_LANGUAGES = ['es', 'en', 'fr', 'pt', 'eo']
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self, language: str = 'en'):
        self.current_language = language if language in self.SUPPORTED_LANGUAGES else self.DEFAULT_LANGUAGE
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Any]:
        """Load translation file for current language"""
        locale_path = os.path.join(os.path.dirname(__file__), 'locales', f'{self.current_language}.json')
        
        try:
            with open(locale_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to English if translation not found
            fallback_path = os.path.join(os.path.dirname(__file__), 'locales', 'en.json')
            with open(fallback_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading translations: {e}")
            return {}
    
    def t(self, key: str, default: str = "") -> str:
        """
        Translate a key to current language
        Usage: i18n.t('audit.title')
        """
        keys = key.split('.')
        value = self.translations
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default if default else key
    
    def get(self, *keys, default: str = "") -> str:
        """Alternative method for translation"""
        return self.t('.'.join(keys), default)
    
    def set_language(self, language: str) -> bool:
        """Change current language"""
        if language in self.SUPPORTED_LANGUAGES:
            self.current_language = language
            self.translations = self._load_translations()
            return True
        return False
    
    def get_all_languages(self) -> Dict[str, str]:
        """Get all supported languages with their names"""
        languages = {}
        for lang_code in self.SUPPORTED_LANGUAGES:
            locale_path = os.path.join(os.path.dirname(__file__), 'locales', f'{lang_code}.json')
            try:
                with open(locale_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    languages[lang_code] = data.get('language', lang_code.upper())
            except:
                languages[lang_code] = lang_code.upper()
        
        return languages


# Global i18n instance
_i18n_instance = None

def get_i18n(language: str = 'en') -> I18nManager:
    """Get or create global i18n instance"""
    global _i18n_instance
    if _i18n_instance is None or _i18n_instance.current_language != language:
        _i18n_instance = I18nManager(language)
    return _i18n_instance


def detect_language_from_domain(url: str) -> str:
    """Detect language from domain/path"""
    url_lower = url.lower()
    
    # Check for language indicators in URL
    if '/es/' in url_lower or '.es' in url_lower or 'spanish' in url_lower:
        return 'es'
    elif '/fr/' in url_lower or '.fr' in url_lower or 'french' in url_lower:
        return 'fr'
    elif '/pt/' in url_lower or '.pt' in url_lower or '.br' in url_lower or 'portuguese' in url_lower:
        return 'pt'
    elif '/eo/' in url_lower or 'esperanto' in url_lower:
        return 'eo'
    else:
        return 'en'  # Default to English


if __name__ == "__main__":
    # Test translations
    for lang in I18nManager.SUPPORTED_LANGUAGES:
        i18n = I18nManager(lang)
        print(f"\n{i18n.t('language')} ({lang}):")
        print(f"  - {i18n.t('audit.title')}")
        print(f"  - {i18n.t('report.title')}")
        print(f"  - {i18n.t('api.welcome')}")
