"""
Language Detection and Translation Utilities
Supports: Uzbek 🇺🇿, Russian 🇷🇺, English 🇬🇧

Module 5: Simple language detection utility
"""
from langdetect import detect, DetectorFactory
from typing import Optional, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set seed for consistent language detection
DetectorFactory.seed = 0


# ============================================================================
# MODULE 5: Simple Language Detection
# ============================================================================

def detect_language_simple(text: str) -> str:
    """
    Simple language detection (Module 5 specification)
    Returns raw language code from langdetect
    
    Args:
        text (str): Text to analyze
    
    Returns:
        str: Language code (e.g., 'en', 'ru', 'uz') or 'en' on error
    
    Example:
        >>> detect_language_simple("Hello world")
        'en'
        >>> detect_language_simple("Привет мир")
        'ru'
    """
    try:
        return detect(text)
    except:
        return "en"


# ============================================================================
# Advanced Language Detection (with mapping)
# ============================================================================

# Supported languages
SUPPORTED_LANGUAGES = {
    'uz': {'name': 'Uzbek', 'flag': '🇺🇿', 'native': "O'zbek"},
    'ru': {'name': 'Russian', 'flag': '🇷🇺', 'native': 'Русский'},
    'en': {'name': 'English', 'flag': '🇬🇧', 'native': 'English'}
}

# Language code mapping (langdetect uses different codes)
LANGUAGE_CODE_MAP = {
    'uz': 'uz',
    'ru': 'ru',
    'en': 'en'
}

# Configure Gemini for translation
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def detect_language(text: str) -> str:
    """
    Detect the language of the given text
    
    Args:
        text (str): Text to analyze
    
    Returns:
        str: Language code ('uz', 'ru', or 'en')
    """
    try:
        detected = detect(text)
        
        # Map detected language to supported languages
        if detected in ['uz', 'tr']:  # Uzbek might be detected as Turkish
            return 'uz'
        elif detected == 'ru':
            return 'ru'
        else:
            return 'en'  # Default to English
    
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'en'  # Default to English on error


def get_language_info(lang_code: str) -> Dict:
    """
    Get information about a language
    
    Args:
        lang_code (str): Language code
    
    Returns:
        Dict: Language information
    """
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])


def translate_text(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    """
    Translate text to target language using Gemini AI
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code ('uz', 'ru', 'en')
        source_lang (str, optional): Source language code
    
    Returns:
        str: Translated text
    """
    # If source and target are the same, return original text
    if source_lang == target_lang:
        return text
    
    target_info = get_language_info(target_lang)
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""Translate the following text to {target_info['native']} ({target_info['name']}).
Provide ONLY the translation, without any explanations or additional text.

Text to translate:
{text}

Translation:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text on error


def get_system_message(lang_code: str, message_key: str) -> str:
    """
    Get system message in the specified language
    
    Args:
        lang_code (str): Language code
        message_key (str): Message identifier
    
    Returns:
        str: Localized message
    """
    messages = {
        'welcome': {
            'uz': "Salom! Men HR yordamchisiman. Sizga qanday yordam bera olaman?",
            'ru': "Здравствуйте! Я HR-ассистент. Чем могу помочь?",
            'en': "Hello! I'm your HR assistant. How can I help you?"
        },
        'error': {
            'uz': "Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            'ru': "Извините, произошла ошибка. Пожалуйста, попробуйте снова.",
            'en': "Sorry, an error occurred. Please try again."
        },
        'no_answer': {
            'uz': "Kechirasiz, bu savolga javob topa olmadim. Iltimos, HR bo'limiga murojaat qiling.",
            'ru': "Извините, я не смог найти ответ на этот вопрос. Пожалуйста, обратитесь в отдел кадров.",
            'en': "Sorry, I couldn't find an answer to this question. Please contact the HR department."
        },
        'processing': {
            'uz': "Javobingizni tayyorlayapman...",
            'ru': "Готовлю ответ...",
            'en': "Preparing your answer..."
        },
        'thank_you': {
            'uz': "Rahmat! Yana savollaringiz bo'lsa, bemalol so'rang.",
            'ru': "Спасибо! Если у вас есть еще вопросы, не стесняйтесь спрашивать.",
            'en': "Thank you! If you have more questions, feel free to ask."
        }
    }
    
    return messages.get(message_key, {}).get(lang_code, messages.get(message_key, {}).get('en', ''))


def format_multilingual_response(answer: str, lang_code: str, include_flag: bool = True) -> str:
    """
    Format response with language indicator
    
    Args:
        answer (str): The answer text
        lang_code (str): Language code
        include_flag (bool): Whether to include language flag
    
    Returns:
        str: Formatted response
    """
    if include_flag:
        lang_info = get_language_info(lang_code)
        return f"{lang_info['flag']} {answer}"
    return answer


def get_greeting(lang_code: str) -> str:
    """
    Get greeting message in specified language
    
    Args:
        lang_code (str): Language code
    
    Returns:
        str: Greeting message
    """
    greetings = {
        'uz': "Assalomu alaykum! Men HR sun'iy intellekt yordamchisiman.",
        'ru': "Здравствуйте! Я AI-ассистент отдела кадров.",
        'en': "Hello! I'm the HR AI assistant."
    }
    return greetings.get(lang_code, greetings['en'])


def create_multilingual_prompt(question: str, context: str, lang_code: str) -> str:
    """
    Create a prompt for Gemini that ensures response in the correct language
    
    Args:
        question (str): User's question
        context (str): Relevant context from documents
        lang_code (str): Target language code
    
    Returns:
        str: Formatted prompt
    """
    lang_info = get_language_info(lang_code)
    
    prompts = {
        'uz': f"""Siz HR bo'limi yordamchisisiz. Quyidagi ma'lumotlar asosida savolga javob bering.

Kontekst (HR hujjatlaridan):
{context}

Savol: {question}

Iltimos, javobni O'zbek tilida bering. Javob aniq, professional va foydali bo'lishi kerak.
Agar kontekstda ma'lumot bo'lmasa, umumiy yordam bering va HR bo'limiga murojaat qilishni tavsiya eting.

Javob:""",
        
        'ru': f"""Вы помощник отдела кадров. Ответьте на вопрос на основе следующей информации.

Контекст (из HR документов):
{context}

Вопрос: {question}

Пожалуйста, дайте ответ на русском языке. Ответ должен быть четким, профессиональным и полезным.
Если в контексте нет информации, дайте общую помощь и порекомендуйте обратиться в отдел кадров.

Ответ:""",
        
        'en': f"""You are an HR department assistant. Answer the question based on the following information.

Context (from HR documents):
{context}

Question: {question}

Please provide the answer in English. The answer should be clear, professional, and helpful.
If the context doesn't have the information, provide general help and recommend contacting the HR department.

Answer:"""
    }
    
    return prompts.get(lang_code, prompts['en'])


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🌍 MULTILINGUAL SUPPORT TEST")
    print("=" * 70)
    
    # Test language detection
    test_texts = {
        "Salom, qanday yordam bera olasiz?": "uz",
        "Здравствуйте, как вы можете помочь?": "ru",
        "Hello, how can you help?": "en"
    }
    
    print("\n📝 Language Detection Test:")
    for text, expected in test_texts.items():
        detected = detect_language(text)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{text[:30]}...' → {detected} (expected: {expected})")
    
    # Test system messages
    print("\n💬 System Messages Test:")
    for lang in ['uz', 'ru', 'en']:
        lang_info = get_language_info(lang)
        greeting = get_greeting(lang)
        print(f"{lang_info['flag']} {lang_info['name']}: {greeting}")
    
    # Test translation (if API key is available)
    print("\n🔄 Translation Test:")
    test_text = "How many vacation days do employees get?"
    for lang in ['uz', 'ru']:
        try:
            translated = translate_text(test_text, lang, 'en')
            lang_info = get_language_info(lang)
            print(f"{lang_info['flag']} {lang_info['name']}: {translated}")
        except Exception as e:
            print(f"❌ Translation to {lang} failed: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Multilingual support module ready!")
    print("=" * 70)
