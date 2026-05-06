"""
RAG (Retrieval-Augmented Generation) Search Module
Implements semantic search over HR documents using embeddings
"""
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from models import HRDoc
from ai_engine import generate_query_embedding
from database import SessionLocal


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1 (List[float]): First vector
        vec2 (List[float]): Second vector
    
    Returns:
        float: Cosine similarity score (0-1)
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def search_similar_documents(
    query: str,
    top_k: int = 3,
    min_similarity: float = 0.3,
    db: Optional[Session] = None
) -> List[Dict[str, any]]:
    """
    Search for documents similar to the query using semantic search
    
    Args:
        query (str): Search query
        top_k (int): Number of top results to return
        min_similarity (float): Minimum similarity threshold
        db (Session, optional): Database session
    
    Returns:
        List[Dict]: List of similar documents with scores
    """
    # Create database session if not provided
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # Generate query embedding
        query_embedding = generate_query_embedding(query)
        
        # Get all documents with embeddings
        docs = db.query(HRDoc).filter(HRDoc.embedding.isnot(None)).all()
        
        if not docs:
            print("⚠️  No documents with embeddings found in database")
            return []
        
        # Calculate similarities
        results = []
        for doc in docs:
            try:
                # Parse embedding from JSON string
                doc_embedding = json.loads(doc.embedding)
                
                # Calculate similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)
                
                # Only include if above threshold
                if similarity >= min_similarity:
                    results.append({
                        'id': doc.id,
                        'title': doc.title,
                        'content': doc.content,
                        'similarity': float(similarity),
                        'created_at': doc.created_at
                    })
            
            except Exception as e:
                print(f"Error processing document {doc.id}: {e}")
                continue
        
        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    finally:
        if close_db:
            db.close()


def get_relevant_context(
    query: str,
    top_k: int = 3,
    max_context_length: int = 2000,
    db: Optional[Session] = None
) -> Tuple[str, List[Dict]]:
    """
    Get relevant context for RAG pipeline
    
    Args:
        query (str): User's query
        top_k (int): Number of documents to retrieve
        max_context_length (int): Maximum total context length
        db (Session, optional): Database session
    
    Returns:
        Tuple[str, List[Dict]]: (context_text, source_documents)
    """
    # Search for similar documents
    similar_docs = search_similar_documents(query, top_k, db=db)
    
    if not similar_docs:
        return "", []
    
    # Build context from similar documents
    context_parts = []
    total_length = 0
    used_docs = []
    
    for doc in similar_docs:
        content = doc['content']
        
        # Truncate if needed to fit within max_context_length
        if total_length + len(content) > max_context_length:
            remaining = max_context_length - total_length
            if remaining > 100:  # Only add if we have meaningful space left
                content = content[:remaining] + "..."
            else:
                break
        
        context_parts.append(f"[{doc['title']}]\n{content}")
        total_length += len(content)
        used_docs.append(doc)
        
        if total_length >= max_context_length:
            break
    
    context = "\n\n".join(context_parts)
    return context, used_docs


def search_documents_by_keyword(
    keyword: str,
    db: Optional[Session] = None
) -> List[Dict[str, any]]:
    """
    Search documents by keyword (fallback for non-embedding search)
    
    Args:
        keyword (str): Keyword to search for
        db (Session, optional): Database session
    
    Returns:
        List[Dict]: Matching documents
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # Search in title and content
        docs = db.query(HRDoc).filter(
            (HRDoc.title.ilike(f'%{keyword}%')) | 
            (HRDoc.content.ilike(f'%{keyword}%'))
        ).all()
        
        results = []
        for doc in docs:
            results.append({
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'created_at': doc.created_at
            })
        
        return results
    
    finally:
        if close_db:
            db.close()


def hybrid_search(
    query: str,
    top_k: int = 3,
    use_semantic: bool = True,
    db: Optional[Session] = None
) -> List[Dict[str, any]]:
    """
    Hybrid search combining semantic and keyword search
    
    Args:
        query (str): Search query
        top_k (int): Number of results to return
        use_semantic (bool): Whether to use semantic search
        db (Session, optional): Database session
    
    Returns:
        List[Dict]: Search results
    """
    if use_semantic:
        # Try semantic search first
        results = search_similar_documents(query, top_k, db=db)
        if results:
            return results
    
    # Fallback to keyword search
    print("ℹ️  Using keyword search fallback")
    keyword_results = search_documents_by_keyword(query, db=db)
    return keyword_results[:top_k]


def get_document_by_id(doc_id: int, db: Optional[Session] = None) -> Optional[Dict]:
    """
    Get a specific document by ID
    
    Args:
        doc_id (int): Document ID
        db (Session, optional): Database session
    
    Returns:
        Optional[Dict]: Document data or None
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        doc = db.query(HRDoc).filter(HRDoc.id == doc_id).first()
        
        if doc:
            return {
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'created_at': doc.created_at,
                'has_embedding': doc.embedding is not None
            }
        return None
    
    finally:
        if close_db:
            db.close()


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🔍 RAG SEARCH TEST")
    print("=" * 70)
    
    # Test 1: Semantic search
    print("\n📊 Test 1: Semantic Search")
    print("-" * 70)
    
    test_queries = [
        "vacation days policy",
        "employee onboarding process",
        "company rules and conduct"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = search_similar_documents(query, top_k=2)
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} (similarity: {result['similarity']:.3f})")
                print(f"     {result['content'][:100]}...")
            print("✅ SUCCESS")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Test 2: Get relevant context
    print("\n" + "=" * 70)
    print("📚 Test 2: Get Relevant Context")
    print("-" * 70)
    
    query = "How many vacation days do I get?"
    try:
        context, sources = get_relevant_context(query, top_k=2)
        print(f"Query: '{query}'")
        print(f"\nContext ({len(context)} chars):")
        print(context[:300] + "...")
        print(f"\nSources: {len(sources)} documents")
        for source in sources:
            print(f"  - {source['title']} (similarity: {source['similarity']:.3f})")
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Keyword search
    print("\n" + "=" * 70)
    print("🔎 Test 3: Keyword Search")
    print("-" * 70)
    
    keyword = "vacation"
    try:
        results = search_documents_by_keyword(keyword)
        print(f"Keyword: '{keyword}'")
        print(f"Found {len(results)} results:")
        for result in results:
            print(f"  - {result['title']}")
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 70)
    print("✅ RAG Search module ready!")
    print("=" * 70)
