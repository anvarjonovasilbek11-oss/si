"""
Google Gemini API client for HR Assistant
Handles AI-powered responses with multilingual support
"""
import google.generativeai as genai
from config import Config
from langdetect import detect, LangDetectException

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

# Model configuration
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Safety settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize model (without system_instruction for older API version)
model = genai.GenerativeModel(
    "gemini-pro",
    generation_config=GENERATION_CONFIG,
    safety_settings=SAFETY_SETTINGS
)


def detect_language(text: str) -> str:
    """
    Detect language of input text
    
    Args:
        text: Input text
        
    Returns:
        Language code ('uz', 'ru', 'en')
    """
    try:
        lang = detect(text)
        
        # Map detected language to supported languages
        if lang in ['uz', 'tr']:  # Uzbek or Turkish (similar)
            return 'uz'
        elif lang == 'ru':
            return 'ru'
        else:
            return 'en'
    except LangDetectException:
        return 'en'  # Default to English


def ask_gemini(prompt: str, lang: str) -> str:
    """
    MODULE 3: Gemini Integration
    Ask Gemini with language-specific prefix
    
    Args:
        prompt: User's question/prompt
        lang: Language code ('uz', 'ru', 'en')
        
    Returns:
        Plain response text from Gemini
    """
    # Language-specific prefixes (no translation API)
    language_prefixes = {
        "uz": "Javobni o'zbek tilida yoz:",
        "ru": "Ответь на русском языке:",
        "en": "Answer in English:"
    }
    
    # Get prefix for language (default to English)
    prefix = language_prefixes.get(lang, language_prefixes["en"])
    
    # Prepend prefix to prompt
    full_prompt = f"{prefix} {prompt}"
    
    try:
        # Send request to Gemini endpoint
        response = model.generate_content(full_prompt)
        
        # Return only the plain response text
        return response.text
    
    except Exception as e:
        print(f"Error in ask_gemini: {e}")
        
        # Return error message in appropriate language
        error_messages = {
            "uz": "Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            "ru": "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз.",
            "en": "Sorry, an error occurred. Please try again."
        }
        
        return error_messages.get(lang, error_messages["en"])


def get_hr_response(question: str) -> dict:
    """
    Get AI response for HR question using ask_gemini
    
    Args:
        question: User's question
        
    Returns:
        Dictionary with answer and detected language
    """
    try:
        # Detect language
        language = detect_language(question)
        
        # Use ask_gemini with language-specific prefix
        answer = ask_gemini(question, language)
        
        return {
            "answer": answer,
            "language": language,
            "success": True
        }
    
    except Exception as e:
        print(f"Error generating response: {e}")
        
        # Return error message in appropriate language
        error_messages = {
            "uz": "Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            "ru": "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз.",
            "en": "Sorry, an error occurred. Please try again."
        }
        
        language = detect_language(question)
        
        return {
            "answer": error_messages.get(language, error_messages["en"]),
            "language": language,
            "success": False,
            "error": str(e)
        }


def get_welcome_message(language: str = "en") -> str:
    """
    Get welcome message in specified language
    
    Args:
        language: Language code ('uz', 'ru', 'en')
        
    Returns:
        Welcome message
    """
    messages = {
        "uz": "Salom! Men HR yordamchisiman. Sizga qanday yordam bera olaman?",
        "ru": "Здравствуйте! Я HR-ассистент. Чем могу вам помочь?",
        "en": "Hello! I'm your HR assistant. How can I help you today?"
    }
    
    return messages.get(language, messages["en"])


if __name__ == "__main__":
    # Test the Gemini client
    print("Testing Gemini HR Assistant Client\n")
    
    test_questions = [
        "How many vacation days do I get?",
        "Сколько дней отпуска я получаю?",
        "Men qancha ta'til kuniga egaman?"
    ]
    
    for question in test_questions:
        print(f"Question: {question}")
        result = get_hr_response(question)
        print(f"Language: {result['language']}")
        print(f"Answer: {result['answer'][:100]}...")
        print("-" * 70)
