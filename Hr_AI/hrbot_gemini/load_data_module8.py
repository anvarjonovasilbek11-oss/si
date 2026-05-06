"""
MODULE 8: Load Initial HR Data
Inserts HR documents with embeddings into the database
"""
import json
import time
from database import SessionLocal
from models import HRDocument
from rag_search_module6 import get_embedding


def load_initial_data():
    """Load initial HR documents into the database"""
    print("=" * 70)
    print("📚 MODULE 8: LOADING INITIAL HR DATA")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(HRDocument).count()
        if existing_count > 0:
            print(f"\n⚠️  Database already has {existing_count} documents")
            response = input("Do you want to add more documents? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return
        
        # HR documents to load
        docs = [
            ("Vacation Policy", "Each employee receives 15 days of annual leave.", "en"),
            ("Mehnat ta'tili siyosati", "Har bir xodim yiliga 15 kun ta'til oladi.", "uz"),
            ("Политика отпуска", "Каждому сотруднику предоставляется 15 дней отпуска в год.", "ru"),
        ]
        
        print(f"\n📄 Loading {len(docs)} HR documents...\n")
        
        success_count = 0
        
        for i, (title, content, lang) in enumerate(docs, 1):
            print(f"[{i}/{len(docs)}] Processing: {title} ({lang.upper()})")
            
            try:
                # Check if document already exists
                existing = db.query(HRDocument).filter(
                    HRDocument.title == title
                ).first()
                
                if existing:
                    print(f"   ⚠️  Document already exists, skipping...")
                    continue
                
                # Generate embedding
                print(f"   Generating embedding...")
                embedding_vector = get_embedding(content)
                
                # Store as JSON
                embedding_json = json.dumps(embedding_vector)
                
                # Create document
                doc = HRDocument(
                    title=title,
                    content=content,
                    language=lang,
                    embedding=embedding_json
                )
                
                db.add(doc)
                db.commit()
                
                print(f"   ✅ Added successfully (ID: {doc.id})")
                success_count += 1
                
                # Delay to avoid rate limits
                if i < len(docs):
                    time.sleep(1)
            
            except Exception as e:
                print(f"   ❌ Error: {e}")
                db.rollback()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 LOADING SUMMARY")
        print("=" * 70)
        print(f"Documents to load: {len(docs)}")
        print(f"✅ Successfully loaded: {success_count}")
        print(f"⏭️  Skipped (already exist): {len(docs) - success_count}")
        
        # Show current database state
        total_docs = db.query(HRDocument).count()
        docs_with_embeddings = db.query(HRDocument).filter(
            HRDocument.embedding.isnot(None)
        ).count()
        
        print(f"\n📚 Database state:")
        print(f"   Total documents: {total_docs}")
        print(f"   With embeddings: {docs_with_embeddings}")
        
        # List all documents
        print(f"\n📋 All documents in database:")
        all_docs = db.query(HRDocument).all()
        for doc in all_docs:
            emb_status = "✓" if doc.embedding else "✗"
            print(f"   {emb_status} [{doc.language.upper()}] {doc.title}")
        
        print("\n✅ Data loading complete!")
    
    finally:
        db.close()


if __name__ == "__main__":
    load_initial_data()
