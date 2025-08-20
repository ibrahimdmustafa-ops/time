#!/bin/bash

# Telegram Bot Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: local, staging, production

set -e  # Exit on any error

ENVIRONMENT=${1:-local}
BOT_TOKEN="8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo"

echo "🚀 Deploying Telegram Bot to $ENVIRONMENT environment..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists pip; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables based on environment
case $ENVIRONMENT in
    "local")
        echo "🏠 Setting up local environment..."
        export BOT_TOKEN="$BOT_TOKEN"
        export LOG_LEVEL="DEBUG"
        ;;
    "staging")
        echo "🧪 Setting up staging environment..."
        export BOT_TOKEN="$BOT_TOKEN"
        export LOG_LEVEL="INFO"
        ;;
    "production")
        echo "🏭 Setting up production environment..."
        export BOT_TOKEN="$BOT_TOKEN"
        export LOG_LEVEL="WARNING"
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Available environments: local, staging, production"
        exit 1
        ;;
esac

# Run tests
echo "🧪 Running tests..."
if command_exists pytest; then
    python -m pytest tests/ -v
else
    echo "⚠️  pytest not found, skipping tests"
fi

# Check bot token validity
echo "🔐 Validating bot token..."
python -c "
import requests
import sys
import os

token = os.getenv('BOT_TOKEN')
if not token:
    print('❌ BOT_TOKEN not set')
    sys.exit(1)

try:
    response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
    if response.status_code == 200:
        bot_info = response.json()
        if bot_info['ok']:
            print(f'✅ Bot token valid: @{bot_info[\"result\"][\"username\"]}')
        else:
            print('❌ Bot token invalid')
            sys.exit(1)
    else:
        print(f'❌ HTTP {response.status_code}: Bot token validation failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Error validating token: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Bot token validation failed"
    exit 1
fi

# Start the bot based on environment
case $ENVIRONMENT in
    "local")
        echo "🚀 Starting bot in local mode..."
        python bot_enhanced.py
        ;;
    "staging"|"production")
        echo "🚀 Starting bot in $ENVIRONMENT mode..."
        # For production, you might want to use a process manager
        if command_exists pm2; then
            pm2 start bot_enhanced.py --name "timezone-bot-$ENVIRONMENT"
            pm2 save
        else
            echo "💡 Consider using PM2 for process management in production"
            python bot_enhanced.py
        fi
        ;;
esac

echo "✅ Deployment completed successfully!"