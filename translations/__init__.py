from typing import Dict, List
import json
import os
from pathlib import Path

class Translator:
    def __init__(self):
        self.current_language = "en"
        self.translations: Dict[str, Dict] = {}
        self.fallback_language = "en"
        self._load_translations()

    def _load_translations(self):
        translations_dir = os.path.dirname(__file__)
        for file in os.listdir(translations_dir):
            if file.endswith('.json'):
                lang = file.split('.')[0]
                with open(os.path.join(translations_dir, file), 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)

    def set_language(self, lang_code: str) -> bool:
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False

    def get(self, key: str, **kwargs) -> str:
        # Get translation with fallback to default language
        translation = self.translations.get(self.current_language, {}).get(key)
        if translation is None:
            translation = self.translations.get(self.fallback_language, {}).get(key, key)
        
        # Handle string formatting
        if kwargs and isinstance(translation, str):
            try:
                return translation.format(**kwargs)
            except KeyError:
                return translation
        return translation

    def get_available_languages(self) -> List[str]:
        return list(self.translations.keys())

    def get_language_name(self, lang_code: str) -> str:
        language_names = {
            "en": "English",
            "es": "Español",
            "fr": "Français"
        }
        return language_names.get(lang_code, lang_code)

    def save_translation(self, lang_code: str, translations: Dict[str, str]) -> bool:
        try:
            file_path = Path(__file__).parent / f"{lang_code}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=4)
            self.translations[lang_code] = translations
            return True
        except Exception:
            return False