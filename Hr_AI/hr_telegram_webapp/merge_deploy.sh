#!/bin/bash

echo "🚀 Merging and Deploying HR Assistant Bot to GitHub"
echo "===================================================="

# Set git user
echo "Setting up git configuration..."
git config user.name "Elbekjon Khayitboev"
git config user.email "backenddevolpment@gmail.com"

# Pull with merge
echo "Pulling existing content..."
git pull origin main --allow-unrelated-histories --no-edit

# Push
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "===================================================="
echo "✅ Deployment Complete!"
echo "===================================================="
echo ""
echo "Your project is now on GitHub:"
echo "https://github.com/KhayitboevElbekjon/HR-Assistant-Chatbot-AI-based-HR-Assistant-for-Employees-"
echo ""
echo "📝 Next steps:"
echo "1. Visit your GitHub repository"
echo "2. Review the merged content"
echo "3. Update README.md if needed"
echo ""
