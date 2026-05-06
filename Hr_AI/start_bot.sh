#!/bin/bash

echo "🚀 Starting HR Assistant Bot Services"
echo "======================================"

# Check if hrbot_gemini is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ hrbot_gemini API already running on port 8000"
else
    echo "Starting hrbot_gemini API on port 8000..."
    cd /home/kali/Music/Hr_AI/hrbot_gemini
    source venv/bin/activate
    nohup python main.py > /tmp/hrbot_gemini.log 2>&1 &
    echo "✅ hrbot_gemini API started"
    sleep 2
fi

# Check if Telegram bot is already running
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Telegram bot already running on port 8001"
else
    echo "Starting Telegram bot on port 8001..."
    cd /home/kali/Music/Hr_AI/hr_telegram_webapp
    source venv/bin/activate
    nohup python main.py > /tmp/telegram_bot.log 2>&1 &
    echo "✅ Telegram bot started"
    sleep 2
fi

echo ""
echo "======================================"
echo "✅ All services are running!"
echo "======================================"
echo ""
echo "📊 Service Status:"
echo "  - hrbot_gemini API: http://localhost:8000"
echo "  - Telegram bot: http://localhost:8001"
echo "  - Bot username: @hr_assistant_aibot"
echo ""
echo "📝 View logs:"
echo "  - hrbot_gemini: tail -f /tmp/hrbot_gemini.log"
echo "  - Telegram bot: tail -f /tmp/telegram_bot.log"
echo ""
echo "🛑 Stop services:"
echo "  - pkill -f 'python main.py'"
echo ""
echo "🧪 Test your bot:"
echo "  1. Open Telegram"
echo "  2. Search: @hr_assistant_aibot"
echo "  3. Send: /start"
echo "  4. Ask questions!"
echo ""
