import json
import os
from typing import Dict, Any

# JSON fayl yo'li
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'uzb.json')

# Global text_manager obyekti
text_manager = None

class TextManager:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.texts = self._load_texts()
    
    def _load_texts(self) -> Dict[str, Dict[str, str]]:
        """JSON faylidan matnlarni yuklash"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Xatolik: JSON fayl yuklanmadi: {e}")
            return {}
    
    def get_text(self, language: str, key: str, **kwargs) -> str:
        """Matnni olish va formatlash"""
        # Fallback til
        fallback_lang = 'uz'
        
        # Matnni olish
        text = None
        
        # Avval berilgan tildan olish
        if language in self.texts and key in self.texts[language]:
            text = self.texts[language][key]
        # Fallback tildan olish
        elif fallback_lang in self.texts and key in self.texts[fallback_lang]:
            text = self.texts[fallback_lang][key]
        else:
            # Agar matn topilmasa, kalitni qaytarish
            return f"[{key}]"
        
        # Formatlash
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError) as e:
            # Agar formatlashda xatolik bo'lsa, oddiy matnni qaytarish
            return text
    
    def reload_texts(self):
        """Matnlarni qayta yuklash"""
        self.texts = self._load_texts()

# Global text_manager obyektini yaratish
def get_text_manager() -> TextManager:
    global text_manager
    if text_manager is None:
        text_manager = TextManager(JSON_FILE_PATH)
    return text_manager

# Qulaylik funksiyasi
def get_text(language: str, key: str, **kwargs) -> str:
    """Matnni olish uchun qulaylik funksiyasi"""
    return get_text_manager().get_text(language, key, **kwargs) 