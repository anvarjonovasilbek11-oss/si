"""
Data Loading and Management Script
Handles loading HR documents and generating embeddings
"""
import os
import sys
from pathlib import Path
from typing import List
import json
import time

from database import SessionLocal, Base, engine
from models import HRDoc, Employee, UserQuery
from ai_engine import generate_embedding


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def load_hr_document(
    title: str,
    content: str,
    generate_emb: bool = True,
    db: SessionLocal = None
) -> bool:
    """
    Load a single HR document into the database
    
    Args:
        title (str): Document title
        content (str): Document content
        generate_emb (bool): Whether to generate embedding
        db: Database session
    
    Returns:
        bool: Success status
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # Check if document exists
        existing = db.query(HRDoc).filter(HRDoc.title == title).first()
        if existing:
            print(f"⚠️  Document '{title}' already exists. Skipping...")
            return False
        
        # Generate embedding if requested
        embedding = None
        if generate_emb:
            try:
                print(f"   Generating embedding for '{title}'...")
                embedding_vector = generate_embedding(content)
                embedding = json.dumps(embedding_vector)
            except Exception as e:
                print(f"   ⚠️  Warning: Could not generate embedding: {e}")
        
        # Create document
        doc = HRDoc(
            title=title,
            content=content,
            embedding=embedding
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        print(f"✅ Loaded: '{title}' (ID: {doc.id})")
        return True
    
    except Exception as e:
        print(f"❌ Error loading document '{title}': {e}")
        db.rollback()
        return False
    
    finally:
        if close_db:
            db.close()


def load_documents_from_folder(
    folder_path: str = "data/hr_docs",
    generate_embeddings: bool = True
) -> dict:
    """
    Load all documents from a folder
    
    Args:
        folder_path (str): Path to documents folder
        generate_embeddings (bool): Whether to generate embeddings
    
    Returns:
        dict: Statistics
    """
    print("=" * 70)
    print("📚 LOADING HR DOCUMENTS")
    print("=" * 70)
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder '{folder_path}' does not exist!")
        return {"total": 0, "success": 0, "failed": 0}
    
    # Get all text files
    doc_files = list(folder.glob("*.txt")) + list(folder.glob("*.md"))
    
    if not doc_files:
        print(f"❌ No documents found in '{folder_path}'")
        return {"total": 0, "success": 0, "failed": 0}
    
    print(f"\n📂 Found {len(doc_files)} document(s)")
    print(f"📊 Embeddings: {'Enabled' if generate_embeddings else 'Disabled'}\n")
    
    db = SessionLocal()
    stats = {"total": len(doc_files), "success": 0, "failed": 0}
    
    try:
        for i, file_path in enumerate(doc_files, 1):
            print(f"[{i}/{len(doc_files)}] Processing: {file_path.name}")
            
            # Read file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                title = file_path.stem.replace('_', ' ').title()
                
                # Load document
                if load_hr_document(title, content, generate_embeddings, db):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                
                # Delay to avoid rate limits
                if generate_embeddings and i < len(doc_files):
                    time.sleep(1)
            
            except Exception as e:
                print(f"❌ Error reading {file_path.name}: {e}")
                stats["failed"] += 1
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 LOADING SUMMARY")
        print("=" * 70)
        print(f"Total documents: {stats['total']}")
        print(f"✅ Successfully loaded: {stats['success']}")
        print(f"❌ Failed: {stats['failed']}")
        
        # Show database state
        total_docs = db.query(HRDoc).count()
        print(f"\n📚 Total documents in database: {total_docs}")
        
        return stats
    
    finally:
        db.close()


def seed_sample_data():
    """Seed database with sample data"""
    print("\n🌱 Seeding sample data...")
    db = SessionLocal()
    
    try:
        # Check if data exists
        if db.query(Employee).first():
            print("⚠️  Sample data already exists. Skipping...")
            return
        
        # Sample employees
        employees = [
            Employee(
                full_name="Alisher Karimov",
                department="Engineering",
                position="Senior Software Engineer",
                hire_date="2020-01-15",
                email="alisher.karimov@company.uz"
            ),
            Employee(
                full_name="Dilnoza Rahimova",
                department="Human Resources",
                position="HR Manager",
                hire_date="2019-03-10",
                email="dilnoza.rahimova@company.uz"
            ),
            Employee(
                full_name="Rustam Tursunov",
                department="Marketing",
                position="Marketing Specialist",
                hire_date="2021-06-01",
                email="rustam.tursunov@company.uz"
            )
        ]
        
        db.add_all(employees)
        db.commit()
        
        print(f"✅ Added {len(employees)} sample employees")
    
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    
    finally:
        db.close()


def show_database_stats():
    """Show database statistics"""
    print("\n" + "=" * 70)
    print("📊 DATABASE STATISTICS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Count records
        employee_count = db.query(Employee).count()
        doc_count = db.query(HRDoc).count()
        query_count = db.query(UserQuery).count()
        
        # Count documents with embeddings
        docs_with_emb = db.query(HRDoc).filter(HRDoc.embedding.isnot(None)).count()
        
        print(f"\n👥 Employees: {employee_count}")
        print(f"📄 HR Documents: {doc_count}")
        print(f"   └─ With embeddings: {docs_with_emb}")
        print(f"💬 User Queries: {query_count}")
        
        # List documents
        if doc_count > 0:
            print("\n📚 Documents:")
            docs = db.query(HRDoc).all()
            for doc in docs:
                emb_status = "✓" if doc.embedding else "✗"
                print(f"   {emb_status} {doc.title} (ID: {doc.id})")
    
    finally:
        db.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load HR data into database")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize database tables"
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load documents from data/hr_docs folder"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed sample employee data"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics"
    )
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Skip generating embeddings"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all operations (init, load, seed)"
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.init, args.load, args.seed, args.stats, args.all]):
        parser.print_help()
        return
    
    try:
        # Initialize tables
        if args.init or args.all:
            create_tables()
        
        # Load documents
        if args.load or args.all:
            load_documents_from_folder(
                generate_embeddings=not args.no_embeddings
            )
        
        # Seed sample data
        if args.seed or args.all:
            seed_sample_data()
        
        # Show statistics
        if args.stats or args.all:
            show_database_stats()
        
        print("\n✅ Operations completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
