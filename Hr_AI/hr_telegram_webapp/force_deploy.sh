#!/bin/bash

echo "🚀 Force Deploying HR Assistant Bot to GitHub"
echo "=============================================="
echo ""
echo "⚠️  WARNING: This will overwrite the remote repository!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Set git user
echo "Setting up git configuration..."
git config user.name "Elbekjon Khayitboev"
git config user.email "backenddevolpment@gmail.com"

# Force push
echo "Force pushing to GitHub..."
git push -u origin main --force

echo ""
echo "=============================================="
echo "✅ Force Deployment Complete!"
echo "=============================================="
echo ""
echo "Your project is now on GitHub:"
echo "https://github.com/KhayitboevElbekjon/HR-Assistant-Chatbot-AI-based-HR-Assistant-for-Employees-"
echo ""
