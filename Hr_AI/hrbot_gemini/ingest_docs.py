"""
HR Document Ingestion Script
Reads HR policy documents from /data/hr_docs folder and stores them in the database
with embeddings for semantic search.
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple
import json
import time

from database import SessionLocal
from models import HRDoc
from gemini_service import embed_text


# Configuration
DOCS_FOLDER = "data/hr_docs"
SUPPORTED_EXTENSIONS = ['.txt', '.md', '.pdf']  # Currently only .txt is fully supported
BATCH_SIZE = 5  # Process documents in batches to avoid rate limits
DELAY_BETWEEN_BATCHES = 2  # Seconds to wait between batches


def get_document_files(folder_path: str) -> List[Path]:
    """
    Get all document files from the specified folder
    
    Args:
        folder_path (str): Path to the documents folder
    
    Returns:
        List[Path]: List of document file paths
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Error: Folder '{folder_path}' does not exist")
        return []
    
    # Get all supported files
    doc_files = []
    for ext in SUPPORTED_EXTENSIONS:
        doc_files.extend(folder.glob(f"*{ext}"))
    
    return sorted(doc_files)


def read_document(file_path: Path) -> Tuple[str, str]:
    """
    Read document content from file
    
    Args:
        file_path (Path): Path to the document file
    
    Returns:
        Tuple[str, str]: (title, content)
    """
    try:
        # Use filename (without extension) as title
        title = file_path.stem.replace('_', ' ').title()
        
        # Read content based on file type
        if file_path.suffix == '.txt' or file_path.suffix == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        else:
            # For other file types, we'd need additional libraries
            print(f"⚠️  Warning: {file_path.suffix} files not fully supported yet")
            return None, None
        
        return title, content
    
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None, None


def document_exists(db, title: str) -> bool:
    """
    Check if a document with the same title already exists
    
    Args:
        db: Database session
        title (str): Document title
    
    Returns:
        bool: True if document exists
    """
    existing = db.query(HRDoc).filter(HRDoc.title == title).first()
    return existing is not None


def ingest_document(db, file_path: Path, generate_embedding: bool = True) -> bool:
    """
    Ingest a single document into the database
    
    Args:
        db: Database session
        file_path (Path): Path to the document file
        generate_embedding (bool): Whether to generate embeddings
    
    Returns:
        bool: True if successful
    """
    # Read document
    title, content = read_document(file_path)
    
    if not title or not content:
        return False
    
    # Check if document already exists
    if document_exists(db, title):
        print(f"⚠️  Document '{title}' already exists. Skipping...")
        return False
    
    # Generate embedding if requested
    embedding = None
    if generate_embedding:
        try:
            print(f"   Generating embedding for '{title}'...")
            embedding_vector = embed_text(content)
            # Convert to JSON string for storage (if not using pgvector)
            embedding = json.dumps(embedding_vector)
        except Exception as e:
            print(f"   ⚠️  Warning: Could not generate embedding: {e}")
            print(f"   Continuing without embedding...")
    
    # Create and save document
    try:
        hr_doc = HRDoc(
            title=title,
            content=content,
            embedding=embedding
        )
        
        db.add(hr_doc)
        db.commit()
        db.refresh(hr_doc)
        
        print(f"✅ Successfully ingested: '{title}' (ID: {hr_doc.id})")
        return True
    
    except Exception as e:
        print(f"❌ Error saving document '{title}': {e}")
        db.rollback()
        return False


def ingest_all_documents(folder_path: str, generate_embeddings: bool = True, 
                         clear_existing: bool = False) -> dict:
    """
    Ingest all documents from the specified folder
    
    Args:
        folder_path (str): Path to the documents folder
        generate_embeddings (bool): Whether to generate embeddings
        clear_existing (bool): Whether to clear existing documents first
    
    Returns:
        dict: Statistics about the ingestion process
    """
    print("=" * 70)
    print("📚 HR DOCUMENT INGESTION")
    print("=" * 70)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Clear existing documents if requested
        if clear_existing:
            print("\n🗑️  Clearing existing documents...")
            count = db.query(HRDoc).delete()
            db.commit()
            print(f"   Deleted {count} existing documents")
        
        # Get document files
        print(f"\n📂 Scanning folder: {folder_path}")
        doc_files = get_document_files(folder_path)
        
        if not doc_files:
            print("❌ No documents found!")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        
        print(f"   Found {len(doc_files)} document(s)")
        
        # Process documents
        stats = {"total": len(doc_files), "success": 0, "failed": 0, "skipped": 0}
        
        print(f"\n📥 Processing documents...")
        print(f"   Embeddings: {'Enabled' if generate_embeddings else 'Disabled'}")
        print()
        
        for i, file_path in enumerate(doc_files, 1):
            print(f"[{i}/{len(doc_files)}] Processing: {file_path.name}")
            
            result = ingest_document(db, file_path, generate_embeddings)
            
            if result:
                stats["success"] += 1
            elif document_exists(db, file_path.stem.replace('_', ' ').title()):
                stats["skipped"] += 1
            else:
                stats["failed"] += 1
            
            # Add delay between documents to avoid rate limits
            if generate_embeddings and i < len(doc_files):
                time.sleep(1)
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 INGESTION SUMMARY")
        print("=" * 70)
        print(f"Total documents found: {stats['total']}")
        print(f"✅ Successfully ingested: {stats['success']}")
        print(f"⏭️  Skipped (already exist): {stats['skipped']}")
        print(f"❌ Failed: {stats['failed']}")
        
        # Show current database state
        total_docs = db.query(HRDoc).count()
        print(f"\n📚 Total documents in database: {total_docs}")
        
        return stats
    
    finally:
        db.close()


def list_documents():
    """List all documents currently in the database"""
    print("=" * 70)
    print("📚 DOCUMENTS IN DATABASE")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        docs = db.query(HRDoc).all()
        
        if not docs:
            print("\nNo documents found in database.")
            return
        
        print(f"\nTotal: {len(docs)} document(s)\n")
        
        for i, doc in enumerate(docs, 1):
            has_embedding = "✓" if doc.embedding else "✗"
            content_preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
            
            print(f"{i}. {doc.title}")
            print(f"   ID: {doc.id}")
            print(f"   Embedding: {has_embedding}")
            print(f"   Content: {content_preview}")
            print(f"   Created: {doc.created_at}")
            print()
    
    finally:
        db.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest HR documents into the database")
    parser.add_argument(
        "--folder",
        default=DOCS_FOLDER,
        help=f"Path to documents folder (default: {DOCS_FOLDER})"
    )
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Skip generating embeddings (faster, but no semantic search)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing documents before ingesting"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all documents in the database"
    )
    
    args = parser.parse_args()
    
    # List documents if requested
    if args.list:
        list_documents()
        return
    
    # Confirm if clearing existing documents
    if args.clear:
        response = input("\n⚠️  This will delete all existing documents. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Run ingestion
    try:
        stats = ingest_all_documents(
            folder_path=args.folder,
            generate_embeddings=not args.no_embeddings,
            clear_existing=args.clear
        )
        
        if stats["success"] > 0:
            print("\n✅ Document ingestion completed successfully!")
        else:
            print("\n⚠️  No new documents were ingested.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
