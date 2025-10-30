# Tender Platform - Платформа-помощник по тендерам

Корпоративная система для автоматизации процесса поиска, анализа и участия в тендерах с использованием искусственного интеллекта.

## Возможности

- 🔍 Автоматический поиск и мониторинг тендеров (ЕИС, коммерческие ЭТП)
- 🤖 AI-анализ тендерной документации
- 📊 Аналитика конкурентов и прогнозирование
- 💰 Финансовый калькулятор с расчётом прибыльности
- 📝 Автоматическая генерация заявок и документов
- ⚖️ Правовая проверка на соответствие законодательству РФ
- 📅 Управление жизненным циклом тендера
- 👥 Совместная работа команды
- 📱 Telegram бот для уведомлений и быстрого доступа

## Технологический стек

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15+
- Redis
- Celery

**Frontend:**
- React 18+ с TypeScript
- Material-UI / Ant Design
- Redux Toolkit

**Telegram Bot:**
- python-telegram-bot
- Async HTTP client

**Инфраструктура:**
- Docker & Docker Compose
- Nginx

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Node.js 18+ (для frontend разработки)

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd tender-platform
```

2. Создайте файл `.env` на основе примера:
```bash
cp backend/.env.example backend/.env
```

3. Отредактируйте `.env` файл и установите необходимые параметры (особенно SECRET_KEY)

4. Запустите сервисы через Docker Compose:
```bash
docker-compose up -d
```

5. Проверьте статус сервисов:
```bash
docker-compose ps
```

6. Откройте приложение:
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Остановка сервисов

```bash
docker-compose down
```

Для удаления данных (volumes):
```bash
docker-compose down -v
```

## Структура проекта

```
tender-platform/
├── backend/              # Backend приложение (FastAPI)
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # SQLAlchemy модели
│   │   ├── schemas/     # Pydantic схемы
│   │   ├── services/    # Бизнес-логика
│   │   ├── tasks/       # Celery задачи
│   │   └── utils/       # Утилиты
│   └── alembic/         # Миграции БД
├── frontend/            # Frontend приложение (React)
├── telegram-bot/        # Telegram бот
│   ├── bot/
│   │   ├── handlers/    # Обработчики команд
│   │   ├── api_client.py # API клиент
│   │   └── keyboards.py  # Клавиатуры
│   └── requirements.txt
├── docs/                # Документация
└── docker-compose.yml   # Docker конфигурация
```

## Telegram Bot

Платформа включает Telegram бота для удобного доступа к функциям системы.

### Настройка Telegram бота

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Настройте `.env` в директории `telegram-bot/`:
```bash
cd telegram-bot
cp .env.example .env
# Укажите TELEGRAM_BOT_TOKEN в .env
```

4. Запустите бота:
```bash
docker-compose up -d telegram_bot
```

Подробная инструкция: [telegram-bot/SETUP.md](telegram-bot/SETUP.md)

### Возможности бота

- 📋 Просмотр актуальных тендеров
- 🔍 Поиск тендеров по ключевым словам
- ⭐ Управление избранным
- 🔔 Настройка уведомлений
- 📊 Быстрая аналитика по тендеру
- ⏰ Напоминания о сроках подачи заявок

Документация: [docs/TELEGRAM_BOT.md](docs/TELEGRAM_BOT.md)

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Telegram Bot

```bash
cd telegram-bot
pip install -r requirements.txt
python -m bot.main
```

### Логи

Логи приложения сохраняются в директории `backend/logs/` с автоматической ротацией.

Просмотр логов в Docker:
```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## Конфигурация

Основные параметры конфигурации находятся в файле `.env`:

- `ENVIRONMENT` - окружение (development/production)
- `DEBUG` - режим отладки
- `SECRET_KEY` - секретный ключ для JWT
- `POSTGRES_*` - параметры подключения к PostgreSQL
- `REDIS_*` - параметры подключения к Redis
- `LOG_LEVEL` - уровень логирования

## Документация API

После запуска приложения документация API доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Лицензия

Proprietary

## Контакты

Для вопросов и поддержки обращайтесь к команде разработки.
