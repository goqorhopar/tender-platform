# Telegram Bot for Tender Platform

Production-grade Telegram bot for tender notifications and user interactions.

## Features

- 📋 Latest tenders view
- 🔔 Subscription management
- ⚙️ Notification settings
- 👤 User profile
- 🔍 Search functionality
- Error handling & logging

## Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Set your bot token in `.env`:
```
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

3. Run with Docker:
```bash
docker-compose up telegram_bot
```

Or run locally:
```bash
pip install -r requirements.txt
python bot.py
```

## Commands

| Command | Description |
|---------|-------------|
| /start | Start the bot |
| /help | Show help |
| /tenders | Latest tenders |
| /subscribe | Subscribe to notifications |
| /unsubscribe | Unsubscribe |
| /profile | View profile |
| /settings | Notification settings |

## Development

The bot uses python-telegram-bot v20+ with async support.

## Production Notes

- Store TELEGRAM_BOT_TOKEN securely
- Use webhook mode for production (not polling)
- Implement Redis for user state storage
- Add rate limiting for API calls
