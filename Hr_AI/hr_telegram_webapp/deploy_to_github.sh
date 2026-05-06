#!/bin/bash

echo "🚀 Deploying HR Assistant Bot to GitHub"
echo "========================================"

# Set git user
echo "Setting up git configuration..."
git config user.name "Elbekjon Khayitboev"
git config user.email "backenddevolpment@gmail.com"

# Add all files
echo "Adding files..."
git add .

# Commit
echo "Committing changes..."
git commit -m "Initial commit: HR Assistant Telegram Bot with RAG integration

Features:
- Telegram bot integration with aiogram
- Google Gemini AI with RAG search
- Multilingual support (UZ/RU/EN)
- PostgreSQL database
- FastAPI backend
- Vector embeddings for smart search
- Complete HR assistant functionality"

# Rename branch to main
echo "Renaming branch to main..."
git branch -M main

# Add remote
echo "Adding GitHub remote..."
git remote add origin https://github.com/KhayitboevElbekjon/HR-Assistant-Chatbot-AI-based-HR-Assistant-for-Employees-.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "Your project is now on GitHub:"
echo "https://github.com/KhayitboevElbekjon/HR-Assistant-Chatbot-AI-based-HR-Assistant-for-Employees-"
echo ""
echo "📝 Next steps:"
echo "1. Visit your GitHub repository"
echo "2. Add a description and topics"
echo "3. Update README.md if needed"
echo "4. Share with others!"
echo ""
