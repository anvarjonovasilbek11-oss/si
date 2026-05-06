#!/bin/bash

echo "🚀 HR Assistant WebApp Bot - Setup Script"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python db.py

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo ""
echo "For more info, see README.md"
