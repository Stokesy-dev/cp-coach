#!/bin/bash
# Exit on failure
set -e

echo "🚀 Setting up CPCoach..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating python virtual environment 'venv'..."
    python3 -m venv venv
fi

echo "📥 Installing/updating Python dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Create .env from template if not present
if [ ! -f ".env" ]; then
    echo "🔑 No .env file found. Copying .env.example..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your actual GROQ_API_KEY."
fi

echo "🎬 Starting CPCoach Streamlit dashboard..."
./venv/bin/streamlit run src/app.py
