#!/bin/bash

# Database setup script for HR Bot
# This script creates the PostgreSQL database and enables pgvector extension

echo "=========================================="
echo "HR Bot Database Setup"
echo "=========================================="

# Database configuration
DB_NAME="hrbot_db"
DB_USER="postgres"

echo ""
echo "Creating database: $DB_NAME"
echo ""

# Create database as the postgres system user
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Database '$DB_NAME' created successfully"
else
    echo "⚠ Database '$DB_NAME' may already exist or there was an error"
fi

# Enable pgvector extension (optional, will fail silently if not installed)
echo ""
echo "Attempting to enable pgvector extension..."
sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ pgvector extension enabled"
else
    echo "⚠ pgvector extension not available (this is optional)"
fi

echo ""
echo "=========================================="
echo "Database setup complete!"
echo "=========================================="
echo ""
echo "You can now run: python init_db.py"
echo "to create tables and seed sample data"
echo ""
