"""
AI Engine for HR Assistant
Handles Gemini API interactions for multilingual responses
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional, Dict
from language_utils import detect_language, create_multilingual_prompt, get_language_info

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Model configurations
GENERATION_MODEL = "gemini-pro-latest"  # Using latest pro model (gemini-1.5-pro not available)
EMBEDDING_MODEL = "models/text-embedding-004"

# Generation configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# Initialize the main model with system instruction
model = genai.GenerativeModel(
    GENERATION_MODEL,
    system_instruction=(
        "You are a helpful HR assistant who can understand and respond fluently "
        "in Uzbek, Russian, and English. Always respond in the same language as the user's input."
    )
)


def get_gemini_response(prompt: str) -> str:
    """
    Get response from Gemini model with system instruction
    Automatically responds in the same language as the input
    
    Args:
        prompt (str): User's question or prompt
    
    Returns:
        str: Generated response in the same language
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        raise


def generate_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using Gemini
    
    Args:
        text (str): Text to embed
    
    Returns:
        List[float]: Embedding vector (768 dimensions)
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise


def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embeddings for search query
    
    Args:
        query (str): Search query
    
    Returns:
        List[float]: Embedding vector (768 dimensions)
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        raise


def generate_answer(
    question: str,
    context: str = "",
    language: Optional[str] = None,
    auto_detect: bool = True
) -> Dict[str, str]:
    """
    Generate answer using Gemini with multilingual support
    
    Args:
        question (str): User's question
        context (str): Relevant context from documents
        language (str, optional): Target language code
        auto_detect (bool): Auto-detect language from question
    
    Returns:
        Dict[str, str]: Response with answer and detected language
    """
    try:
        # Detect language if not provided
        if auto_detect and not language:
            language = detect_language(question)
        elif not language:
            language = 'en'
        
        # Get language info
        lang_info = get_language_info(language)
        
        # Create multilingual prompt
        prompt = create_multilingual_prompt(question, context, language)
        
        # Initialize model
        model = genai.GenerativeModel(
            model_name=GENERATION_MODEL,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Generate response
        response = model.generate_content(prompt)
        
        if response.text:
            return {
                "answer": response.text.strip(),
                "language": language,
                "language_name": lang_info['name'],
                "flag": lang_info['flag']
            }
        else:
            return {
                "answer": "Sorry, I couldn't generate a response.",
                "language": language,
                "language_name": lang_info['name'],
                "flag": lang_info['flag']
            }
    
    except Exception as e:
        print(f"Error generating answer: {e}")
        raise


def generate_hr_answer(
    question: str,
    relevant_docs: List[str] = None,
    language: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate HR-specific answer with context from relevant documents
    
    Args:
        question (str): User's HR question
        relevant_docs (List[str]): List of relevant document contents
        language (str, optional): Target language code
    
    Returns:
        Dict[str, str]: Response with answer and metadata
    """
    # Build context from relevant documents
    context = ""
    if relevant_docs:
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(relevant_docs)])
    
    # Generate answer
    return generate_answer(question, context, language)


def chat_with_context(
    question: str,
    context_docs: List[Dict[str, str]],
    language: Optional[str] = None
) -> Dict[str, str]:
    """
    Chat with context from multiple documents
    
    Args:
        question (str): User's question
        context_docs (List[Dict]): List of documents with title and content
        language (str, optional): Target language code
    
    Returns:
        Dict[str, str]: Response with answer and metadata
    """
    # Format context with document titles
    context_parts = []
    for doc in context_docs:
        title = doc.get('title', 'Document')
        content = doc.get('content', '')
        context_parts.append(f"=== {title} ===\n{content}")
    
    context = "\n\n".join(context_parts)
    
    # Generate answer
    return generate_answer(question, context, language)


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🤖 AI ENGINE TEST")
    print("=" * 70)
    
    # Test 1: Multilingual answer generation
    print("\n📝 Test 1: Multilingual Answer Generation")
    print("-" * 70)
    
    test_questions = [
        ("How many vacation days do employees get?", "en"),
        ("Сколько дней отпуска получают сотрудники?", "ru"),
        ("Xodimlar necha kun ta'til oladi?", "uz")
    ]
    
    for question, expected_lang in test_questions:
        print(f"\nQuestion: {question}")
        try:
            result = generate_answer(question, auto_detect=True)
            print(f"Detected: {result['flag']} {result['language_name']}")
            print(f"Answer: {result['answer'][:150]}...")
            print("✅ SUCCESS")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Test 2: Answer with context
    print("\n" + "=" * 70)
    print("📚 Test 2: Answer with Context")
    print("-" * 70)
    
    context = "Employees are entitled to 15 days of paid leave per year."
    question = "How many vacation days?"
    
    try:
        result = generate_hr_answer(question, [context], language='en')
        print(f"Question: {question}")
        print(f"Context: {context}")
        print(f"Answer: {result['answer']}")
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 70)
    print("✅ AI Engine ready!")
    print("=" * 70)
