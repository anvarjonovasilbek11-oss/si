#!/bin/bash

# Setup script for bot token configuration
echo "🤖 Setting up HR Assistant WebApp Bot"
echo "======================================"

# Create .env file with your bot token
cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8476485506:AAGtc9SGqx60Y344vLCQcVEF7RZif--5yOA

# Google Gemini API (ADD YOUR KEY HERE)
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hr_telegram_bot

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
WEBAPP_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
EOF

echo "✅ .env file created with bot token"
echo ""
echo "⚠️  IMPORTANT: Add your Gemini API key to .env file"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Make sure PostgreSQL is running"
echo "3. Run: python db.py (to initialize database)"
echo "4. Run: python main.py (to start the bot)"
echo ""
echo "To get Gemini API key:"
echo "Visit: https://makersuite.google.com/app/apikey"
