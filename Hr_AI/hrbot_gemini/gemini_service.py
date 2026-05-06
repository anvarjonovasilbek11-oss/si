"""
Gemini API Service for HR Bot
Provides text generation and embedding capabilities using Google's Gemini AI
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)

# Model configurations
GENERATION_MODEL = "gemini-2.0-flash"  # Updated to available model
EMBEDDING_MODEL = "models/text-embedding-004"  # Updated embedding model

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


def generate_answer(prompt: str, context: Optional[str] = None) -> str:
    """
    Generate an answer using Gemini 1.5 Flash model
    
    Args:
        prompt (str): The user's question or prompt
        context (str, optional): Additional context to help generate better answers
    
    Returns:
        str: The generated text response
    
    Raises:
        Exception: If the API call fails
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel(
            model_name=GENERATION_MODEL,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Prepare the full prompt with context if provided
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        
        # Generate content
        response = model.generate_content(full_prompt)
        
        # Extract and return the text
        if response.text:
            return response.text.strip()
        else:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
    
    except Exception as e:
        print(f"Error generating answer: {e}")
        raise Exception(f"Failed to generate answer: {str(e)}")


def embed_text(text: str) -> List[float]:
    """
    Generate embeddings for the given text using Gemini embedding model
    
    Args:
        text (str): The text to embed
    
    Returns:
        List[float]: The embedding vector (768 dimensions)
    
    Raises:
        Exception: If the API call fails
    """
    try:
        # Generate embedding
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        
        # Return the embedding vector
        return result['embedding']
    
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise Exception(f"Failed to generate embedding: {str(e)}")


def embed_query(query: str) -> List[float]:
    """
    Generate embeddings for a search query
    
    Args:
        query (str): The search query to embed
    
    Returns:
        List[float]: The embedding vector (768 dimensions)
    
    Raises:
        Exception: If the API call fails
    """
    try:
        # Generate embedding with query task type
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        
        # Return the embedding vector
        return result['embedding']
    
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        raise Exception(f"Failed to generate query embedding: {str(e)}")


def generate_hr_response(question: str, relevant_docs: List[str] = None) -> str:
    """
    Generate an HR-specific response using context from relevant documents
    
    Args:
        question (str): The user's HR-related question
        relevant_docs (List[str], optional): List of relevant HR document contents
    
    Returns:
        str: The generated HR response
    """
    # Build context from relevant documents
    context = ""
    if relevant_docs:
        context = "Relevant HR Information:\n\n"
        for i, doc in enumerate(relevant_docs, 1):
            context += f"{i}. {doc}\n\n"
    
    # Create HR-focused prompt
    hr_prompt = f"""You are an HR assistant chatbot. Answer the following question based on the provided HR information.
If the information is not available in the context, provide a general helpful response but mention that specific company policy should be verified with HR.

{context}
Question: {question}

Please provide a clear, professional, and helpful answer:"""
    
    return generate_answer(hr_prompt)


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Gemini API Service")
    print("=" * 60)
    
    # Test 1: Generate Answer
    print("\n📝 Test 1: Generate Answer")
    print("-" * 60)
    test_prompt = "What are the benefits of working in a team?"
    print(f"Prompt: {test_prompt}")
    try:
        answer = generate_answer(test_prompt)
        print(f"\nAnswer:\n{answer}")
        print("\n✅ Answer generation successful!")
    except Exception as e:
        print(f"\n❌ Answer generation failed: {e}")
    
    # Test 2: Embed Text
    print("\n" + "=" * 60)
    print("📊 Test 2: Embed Text")
    print("-" * 60)
    test_text = "Employee leave policy and vacation days"
    print(f"Text: {test_text}")
    try:
        embedding = embed_text(test_text)
        print(f"\nEmbedding dimension: {len(embedding)}")
        print(f"First 10 values: {embedding[:10]}")
        print("\n✅ Text embedding successful!")
    except Exception as e:
        print(f"\n❌ Text embedding failed: {e}")
    
    # Test 3: HR Response with Context
    print("\n" + "=" * 60)
    print("💼 Test 3: HR Response with Context")
    print("-" * 60)
    hr_question = "How many vacation days do employees get?"
    hr_context = ["Employees are entitled to 15 days of paid leave per year."]
    print(f"Question: {hr_question}")
    try:
        hr_answer = generate_hr_response(hr_question, hr_context)
        print(f"\nHR Answer:\n{hr_answer}")
        print("\n✅ HR response generation successful!")
    except Exception as e:
        print(f"\n❌ HR response generation failed: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
