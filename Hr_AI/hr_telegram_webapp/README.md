# HR Assistant WebApp Bot (MVP)

Multilingual HR chatbot that runs inside Telegram as a WebApp, powered by FastAPI, aiogram, and Google Gemini AI.

## 🎯 Features

- **Telegram WebApp Integration** - Chat interface inside Telegram
- **Multilingual Support** - Uzbek 🇺🇿, Russian 🇷🇺, English 🇬🇧
- **AI-Powered Responses** - Google Gemini API for intelligent answers
- **Chat History** - PostgreSQL database for conversation logs
- **Modern UI** - Responsive design with Telegram theme colors

## 🛠️ Tech Stack

- **Backend**: FastAPI + aiogram
- **AI**: Google Gemini API
- **Database**: PostgreSQL + SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript (Telegram WebApp)

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd hr_telegram_webapp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/hr_telegram_bot
WEBAPP_URL=https://your-domain.com
```

### 3. Initialize Database

```bash
python db.py
```

### 4. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

## 📱 Telegram Bot Setup

1. **Create Bot** with [@BotFather](https://t.me/botfather)
   ```
   /newbot
   ```

2. **Set Bot Commands**
   ```
   /setcommands
   start - Start the HR Assistant
   help - Show help information
   ```

3. **Configure WebApp URL**
   - Set your domain in `.env` as `WEBAPP_URL`
   - For local testing, use ngrok: `ngrok http 8000`

4. **Test Your Bot**
   - Open your bot in Telegram
   - Send `/start`
   - Click "Open HR Assistant" button

## 📁 Project Structure

```
hr_telegram_webapp/
├── main.py              # FastAPI application
├── telegram_bot.py      # Telegram bot with aiogram
├── gemini_client.py     # Google Gemini API client
├── db.py                # Database configuration
├── models.py            # SQLAlchemy models
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── static/
│   ├── webapp.html      # WebApp UI
│   ├── css/
│   │   └── style.css    # Styles
│   └── js/
│       └── app.js       # WebApp logic
└── README.md
```

## 🔌 API Endpoints

### Chat
```bash
POST /api/chat
{
  "telegram_id": 123456789,
  "question": "How many vacation days?"
}
```

### History
```bash
GET /api/history/{telegram_id}?limit=10
```

### User Info
```bash
GET /api/user/{telegram_id}
```

## 🌍 Supported Languages

The bot automatically detects and responds in:
- **Uzbek** (uz)
- **Russian** (ru)
- **English** (en)

## 🎨 WebApp Features

- **Responsive Design** - Works on all devices
- **Telegram Theme Integration** - Matches user's Telegram theme
- **Chat History** - Loads previous conversations
- **Real-time Messaging** - Instant AI responses
- **Haptic Feedback** - Native Telegram feedback

## 🔧 Development

### Run in Development Mode

```bash
# Terminal 1: Run FastAPI with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Run Telegram bot separately (optional)
python telegram_bot.py
```

### Test Gemini Client

```bash
python gemini_client.py
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## 📊 Database Schema

### Users Table
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username
- `first_name`, `last_name` - User names
- `language_code` - Preferred language

### Chat Logs Table
- `telegram_id` - User ID
- `question` - User's question
- `answer` - Bot's response
- `language` - Detected language
- `created_at` - Timestamp

## 🚀 Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Using Systemd

Create `/etc/systemd/system/hr-bot.service`:

```ini
[Unit]
Description=HR Assistant WebApp Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/hr_telegram_webapp
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/hr_telegram_webapp/static;
    }
}
```

## 🐛 Troubleshooting

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Verify bot is running: `ps aux | grep python`
- Check logs for errors

### WebApp not loading
- Verify `WEBAPP_URL` is accessible
- Check CORS settings in `main.py`
- Ensure static files are served correctly

### Database connection errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Run `python db.py` to initialize

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for HR teams**
