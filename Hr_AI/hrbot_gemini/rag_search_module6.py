"""
MODULE 6: RAG (Retrieval-Augmented Generation) Search
Context retrieval for HR documents using embeddings

Note: This module provides two implementations:
1. Current: JSON-based embeddings (working now)
2. pgvector: Native vector search (requires pgvector extension)
"""
import json
import numpy as np
from sqlalchemy import text
from database import SessionLocal
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Tuple

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ============================================================================
# MODULE 6: Core Functions (As Specified)
# ============================================================================

def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Gemini
    
    Args:
        text (str): Text to embed
    
    Returns:
        List[float]: Embedding vector
    """
    result = genai.embed_content(
        model="models/text-embedding-004",  # Updated model
        content=text
    )
    return result["embedding"]


def search_hr_docs(query: str, limit: int = 3) -> List[Tuple]:
    """
    Search HR documents using embeddings (Module 6 specification)
    
    This is the pgvector version - requires pgvector extension installed.
    For current setup without pgvector, use search_hr_docs_json() instead.
    
    Args:
        query (str): Search query
        limit (int): Number of results to return
    
    Returns:
        List[Tuple]: List of (id, title, content, language) tuples
    """
    db = SessionLocal()
    
    try:
        query_embedding = get_embedding(query)
        
        # This requires pgvector extension
        rows = db.execute(text("""
            SELECT id, title, content, language
            FROM hr_documents
            ORDER BY embedding <-> :query_embedding
            LIMIT :limit
        """), {
            "query_embedding": query_embedding,
            "limit": limit
        }).fetchall()
        
        return rows
    
    finally:
        db.close()


# ============================================================================
# Current Implementation (JSON-based embeddings)
# ============================================================================

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def search_hr_docs_json(query: str, limit: int = 3) -> List[Dict]:
    """
    Search HR documents using JSON-stored embeddings (Current implementation)
    
    This works with the current setup where embeddings are stored as JSON text.
    
    Args:
        query (str): Search query
        limit (int): Number of results to return
    
    Returns:
        List[Dict]: List of document dictionaries with similarity scores
    """
    db = SessionLocal()
    
    try:
        # Generate query embedding
        query_embedding = get_embedding(query)
        
        # Get all documents with embeddings
        rows = db.execute(text("""
            SELECT id, title, content, language, embedding
            FROM hr_documents
            WHERE embedding IS NOT NULL
        """)).fetchall()
        
        # Calculate similarities
        results = []
        for row in rows:
            try:
                # Parse JSON embedding
                doc_embedding = json.loads(row.embedding)
                
                # Calculate similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)
                
                results.append({
                    'id': row.id,
                    'title': row.title,
                    'content': row.content,
                    'language': row.language,
                    'similarity': similarity
                })
            except Exception as e:
                print(f"Error processing document {row.id}: {e}")
                continue
        
        # Sort by similarity (descending) and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    finally:
        db.close()


def search_hr_docs_by_language(query: str, language: str, limit: int = 3) -> List[Dict]:
    """
    Search HR documents filtered by language
    
    Args:
        query (str): Search query
        language (str): Language code ('uz', 'ru', 'en')
        limit (int): Number of results to return
    
    Returns:
        List[Dict]: List of document dictionaries
    """
    db = SessionLocal()
    
    try:
        query_embedding = get_embedding(query)
        
        # Get documents in specific language
        rows = db.execute(text("""
            SELECT id, title, content, language, embedding
            FROM hr_documents
            WHERE embedding IS NOT NULL AND language = :language
        """), {"language": language}).fetchall()
        
        # Calculate similarities
        results = []
        for row in rows:
            try:
                doc_embedding = json.loads(row.embedding)
                similarity = cosine_similarity(query_embedding, doc_embedding)
                
                results.append({
                    'id': row.id,
                    'title': row.title,
                    'content': row.content,
                    'language': row.language,
                    'similarity': similarity
                })
            except Exception as e:
                print(f"Error processing document {row.id}: {e}")
                continue
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    finally:
        db.close()


def get_context_for_query(query: str, language: str = None, limit: int = 3) -> Tuple[str, List[Dict]]:
    """
    Get formatted context for RAG pipeline
    
    Args:
        query (str): User's query
        language (str, optional): Filter by language
        limit (int): Number of documents to retrieve
    
    Returns:
        Tuple[str, List[Dict]]: (formatted_context, source_documents)
    """
    # Search documents
    if language:
        docs = search_hr_docs_by_language(query, language, limit)
    else:
        docs = search_hr_docs_json(query, limit)
    
    if not docs:
        return "", []
    
    # Format context
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(
            f"Document {i}: {doc['title']}\n"
            f"Language: {doc['language'].upper()}\n"
            f"{doc['content']}\n"
        )
    
    context = "\n---\n".join(context_parts)
    return context, docs


# ============================================================================
# Test Functions
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 MODULE 6: RAG SEARCH TEST")
    print("=" * 70)
    
    # Test 1: Get embedding
    print("\n📊 Test 1: Get Embedding")
    print("-" * 70)
    test_text = "vacation policy"
    try:
        embedding = get_embedding(test_text)
        print(f"Text: '{test_text}'")
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Search HR documents (JSON-based)
    print("\n" + "=" * 70)
    print("📚 Test 2: Search HR Documents (JSON-based)")
    print("-" * 70)
    
    test_queries = [
        "vacation days",
        "отпуск",  # Russian: vacation
        "ta'til"   # Uzbek: vacation
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = search_hr_docs_json(query, limit=2)
            print(f"Found {len(results)} results:")
            for i, doc in enumerate(results, 1):
                print(f"  {i}. {doc['title']} ({doc['language'].upper()})")
                print(f"     Similarity: {doc['similarity']:.3f}")
            print("✅ SUCCESS")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Test 3: Get context for query
    print("\n" + "=" * 70)
    print("📝 Test 3: Get Context for Query")
    print("-" * 70)
    
    query = "How many vacation days?"
    try:
        context, sources = get_context_for_query(query, limit=2)
        print(f"Query: '{query}'")
        print(f"\nContext ({len(context)} chars):")
        print(context[:300] + "...")
        print(f"\nSources: {len(sources)} documents")
        for source in sources:
            print(f"  - {source['title']} (similarity: {source['similarity']:.3f})")
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 70)
    print("✅ MODULE 6 TESTING COMPLETE")
    print("=" * 70)
    print("\nFunctions available:")
    print("  - get_embedding(text)")
    print("  - search_hr_docs_json(query, limit=3)")
    print("  - search_hr_docs_by_language(query, language, limit=3)")
    print("  - get_context_for_query(query, language=None, limit=3)")
