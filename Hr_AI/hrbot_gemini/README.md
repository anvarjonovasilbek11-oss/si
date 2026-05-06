# HR Bot with Gemini AI

An AI-powered HR chatbot built with FastAPI and Google Gemini.

## Project Setup

### 1. Create Virtual Environment

```bash
cd hrbot_gemini
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

The `.env` file is already created with the following variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `DATABASE_URL`: PostgreSQL database connection string

**Note:** Make sure PostgreSQL is running and the database `hrbot_db` exists.

### 4. Create Database (if not exists)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE hrbot_db;
\q
```

### 5. Run the Application

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

### 6. Test the Application

Open your browser and navigate to:
- API Documentation: http://localhost:8000/docs
- Test endpoint: http://localhost:8000/ping (should return `{"message": "pong"}`)
- Root endpoint: http://localhost:8000/

## API Endpoints

- `GET /` - Root endpoint with status information
- `GET /ping` - Health check endpoint

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **google-generativeai**: Google Gemini AI SDK
- **psycopg2-binary**: PostgreSQL adapter for Python
- **sqlalchemy**: SQL toolkit and ORM
- **python-dotenv**: Environment variable management
- **qdrant-client**: Vector database client
- **pgvector**: PostgreSQL vector extension support

## Project Structure

```
hrbot_gemini/
├── main.py                 # FastAPI application entry point
├── database.py             # Database connection and session management
├── models.py               # SQLAlchemy database models
├── gemini_service.py       # Gemini AI integration service
├── ingest_docs.py          # HR document ingestion script
├── init_db.py              # Database initialization script
├── test_gemini.py          # Comprehensive Gemini API tests
├── test_gemini_simple.py   # Simple Gemini API test
├── setup_database.sh       # Database setup script
├── data/
│   └── hr_docs/            # HR policy documents
│       ├── vacation_policy.txt
│       ├── company_rules.txt
│       └── onboarding_steps.txt
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore              # Git ignore rules
├── DATABASE_SETUP.md       # Database configuration guide
├── INGESTION_GUIDE.md      # Document ingestion guide
└── README.md               # This file
```

## Database Models

### Employee
- Employee information (name, department, position, hire date, email)

### HRDoc
- HR documents with content and embeddings for semantic search

### UserQuery
- User query history with questions and answers

## Gemini AI Integration

The `gemini_service.py` module provides:

- **`generate_answer(prompt, context)`** - Generate AI responses using Gemini 2.0 Flash
- **`embed_text(text)`** - Generate embeddings for documents (768 dimensions)
- **`embed_query(query)`** - Generate embeddings for search queries
- **`generate_hr_response(question, relevant_docs)`** - Context-aware HR responses

### Test Gemini Service

```bash
# Simple test (recommended)
python test_gemini_simple.py

# Comprehensive test (may hit rate limits)
python test_gemini.py
```

## Initialize Database

```bash
# Run database initialization
python init_db.py
```

This will:
- Create all database tables
- Seed sample data (3 employees, 3 HR docs, 1 query)
- Verify the setup

## Ingest HR Documents

Add HR policy documents to the database with embeddings:

```bash
# Ingest all documents from data/hr_docs/
python ingest_docs.py

# List documents in database
python ingest_docs.py --list

# See full guide
cat INGESTION_GUIDE.md
```

The script will:
- Read documents from `data/hr_docs/` folder
- Generate embeddings using Gemini AI
- Store in PostgreSQL for semantic search

Sample documents included:
- Vacation Policy
- Company Rules
- Onboarding Steps

## Next Steps

1. ✅ Set up database models with SQLAlchemy
2. ✅ Integrate Google Gemini AI
3. ✅ Implement document ingestion with embeddings
4. Build HR chatbot endpoints with semantic search
5. Add authentication and authorization
