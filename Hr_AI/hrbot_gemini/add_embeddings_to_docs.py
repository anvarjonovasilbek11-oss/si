"""
Add embeddings to hr_documents table
Generates embeddings for documents that don't have them
"""
import json
import time
from database import SessionLocal
from models import HRDocument
from rag_search_module6 import get_embedding


def add_embeddings_to_documents():
    """Add embeddings to all documents without them"""
    print("=" * 70)
    print("🔧 ADDING EMBEDDINGS TO HR DOCUMENTS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Get documents without embeddings
        docs_without_embeddings = db.query(HRDocument).filter(
            HRDocument.embedding.is_(None)
        ).all()
        
        if not docs_without_embeddings:
            print("\n✅ All documents already have embeddings!")
            return
        
        print(f"\n📄 Found {len(docs_without_embeddings)} documents without embeddings\n")
        
        success_count = 0
        
        for i, doc in enumerate(docs_without_embeddings, 1):
            print(f"[{i}/{len(docs_without_embeddings)}] Processing: {doc.title} ({doc.language})")
            
            try:
                # Generate embedding
                print(f"   Generating embedding...")
                embedding_vector = get_embedding(doc.content)
                
                # Store as JSON
                doc.embedding = json.dumps(embedding_vector)
                
                db.commit()
                print(f"   ✅ Embedding added ({len(embedding_vector)} dimensions)")
                success_count += 1
                
                # Delay to avoid rate limits
                if i < len(docs_without_embeddings):
                    time.sleep(1)
            
            except Exception as e:
                print(f"   ❌ Error: {e}")
                db.rollback()
        
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"Total documents: {len(docs_without_embeddings)}")
        print(f"✅ Successfully added embeddings: {success_count}")
        print(f"❌ Failed: {len(docs_without_embeddings) - success_count}")
        
        # Show current state
        total_docs = db.query(HRDocument).count()
        docs_with_embeddings = db.query(HRDocument).filter(
            HRDocument.embedding.isnot(None)
        ).count()
        
        print(f"\n📚 Database state:")
        print(f"   Total documents: {total_docs}")
        print(f"   With embeddings: {docs_with_embeddings}")
        print(f"   Without embeddings: {total_docs - docs_with_embeddings}")
    
    finally:
        db.close()


if __name__ == "__main__":
    add_embeddings_to_documents()
