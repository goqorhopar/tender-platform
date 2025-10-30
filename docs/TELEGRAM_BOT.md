# Telegram Bot - Документация

## Обзор

Telegram бот предоставляет пользователям удобный интерфейс для работы с платформой-помощником по тендерам прямо из мессенджера.

## Основные возможности

### 1. Регистрация и привязка аккаунта (/start)

Пользователь может привязать свой аккаунт платформы к Telegram:
- Вводит email
- Вводит пароль (сообщение автоматически удаляется)
- Аккаунт привязывается к telegram_chat_id

### 2. Просмотр тендеров (/tenders)

- Список актуальных тендеров с основной информацией
- Краткая карточка тендера: название, заказчик, бюджет, сроки
- Inline-кнопки для быстрых действий

### 3. Поиск тендеров (/search)

- Поиск по ключевым словам
- Результаты с возможностью просмотра деталей
- Можно искать через команду или просто отправив текст

### 4. Работа с тендерами

Для каждого тендера доступны действия:
- ⭐ Добавить в избранное / Удалить из избранного
- 📊 Запросить аналитику
- ❌ Отклонить тендер
- 🌐 Открыть в веб-интерфейсе

### 5. Уведомления (/notifications)

Настройка уведомлений:
- 🔔 Новые релевантные тендеры
- ⏰ Напоминания о приближающихся сроках
- 📈 Изменения статуса тендеров
- 👥 Новые конкуренты

### 6. Аналитика

Быстрая аналитика по тендеру:
- Количество конкурентов
- Вероятность выигрыша
- Средняя цена в нише
- Диапазон цен

## Архитектура

### Структура проекта

```
telegram-bot/
├── bot/
│   ├── main.py              # Точка входа, регистрация handlers
│   ├── config.py            # Конфигурация бота
│   ├── api_client.py        # HTTP клиент для backend API
│   ├── keyboards.py         # Клавиатуры и inline-кнопки
│   └── handlers/
│       ├── start.py         # Регистрация, /start, /help
│       ├── tenders.py       # Работа с тендерами
│       └── notifications.py # Уведомления
├── requirements.txt
├── Dockerfile
└── .env
```

### Взаимодействие с Backend

Бот использует REST API backend для:

1. **Аутентификация**
   - POST `/api/v1/auth/login` - вход пользователя
   - PUT `/api/v1/users/me` - обновление telegram_chat_id

2. **Пользователи**
   - GET `/api/v1/users/by-telegram/{chat_id}` - получение пользователя по chat_id

3. **Тендеры**
   - GET `/api/v1/tenders` - список тендеров
   - POST `/api/v1/tenders/search` - поиск
   - GET `/api/v1/tenders/{id}` - детали тендера
   - POST `/api/v1/tenders/{id}/favorite` - добавить в избранное
   - DELETE `/api/v1/tenders/{id}/favorite` - удалить из избранного

4. **Аналитика**
   - GET `/api/v1/analytics/tender/{id}` - аналитика по тендеру

5. **Уведомления**
   - GET `/api/v1/notifications/settings` - получить настройки
   - PUT `/api/v1/notifications/settings` - обновить настройки

## Установка и запуск

### Предварительные требования

1. Создать бота через [@BotFather](https://t.me/botfather)
2. Получить токен бота
3. Backend API должен быть запущен

### Настройка

1. Создайте файл `.env` в директории `telegram-bot/`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
BACKEND_API_URL=http://backend:8000
API_V1_PREFIX=/api/v1
ENVIRONMENT=development
DEBUG=true
```

2. Для production используйте `.env.production`:

```env
TELEGRAM_BOT_TOKEN=your_production_bot_token
BACKEND_API_URL=https://api.yourplatform.com
API_V1_PREFIX=/api/v1
ENVIRONMENT=production
DEBUG=false
```

### Запуск с Docker Compose

Бот автоматически запускается вместе с остальными сервисами:

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов бота
docker-compose logs -f telegram_bot

# Перезапуск бота
docker-compose restart telegram_bot
```

### Локальный запуск (для разработки)

```bash
cd telegram-bot

# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
python -m bot.main
```

## Разработка

### Добавление новой команды

1. Создайте handler в соответствующем файле или новом:

```python
# bot/handlers/my_feature.py
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mycommand"""
    await update.message.reply_text("Hello from my command!")
```

2. Зарегистрируйте handler в `bot/main.py`:

```python
from bot.handlers.my_feature import my_command

# В функции main()
application.add_handler(CommandHandler("mycommand", my_command))
```

### Добавление inline-кнопок

1. Создайте клавиатуру в `bot/keyboards.py`:

```python
def get_my_keyboard():
    buttons = [
        [InlineKeyboardButton("Кнопка 1", callback_data="action_1")],
        [InlineKeyboardButton("Кнопка 2", callback_data="action_2")]
    ]
    return InlineKeyboardMarkup(buttons)
```

2. Создайте callback handler:

```python
async def handle_my_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "action_1":
        await query.edit_message_text("Вы нажали кнопку 1")
```

3. Зарегистрируйте callback handler:

```python
application.add_handler(CallbackQueryHandler(handle_my_callback, pattern="^action_"))
```

### Добавление API метода

Добавьте метод в `bot/api_client.py`:

```python
async def my_api_method(self, chat_id: str, param: str) -> Dict[str, Any]:
    """My API method description"""
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(
            f"{self.base_url}/my-endpoint/{param}",
            headers={"X-Telegram-Chat-ID": chat_id}
        )
        response.raise_for_status()
        return response.json()
```

## Отправка уведомлений из Backend

Backend может отправлять уведомления пользователям через Telegram:

```python
# В backend Celery task
from app.integrations.telegram import send_telegram_notification

@celery_app.task
def send_tender_notification(user_id: str, tender_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user.telegram_chat_id:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        
        notification = {
            "type": "new_tender",
            "title": "Новый тендер",
            "message": f"Найден новый тендер: {tender.title}",
            "related_tender_id": str(tender_id)
        }
        
        send_telegram_notification(user.telegram_chat_id, notification)
```

## Безопасность

### Хранение токенов

- Токен бота хранится в переменных окружения
- Никогда не коммитьте `.env` файлы в git
- Используйте разные токены для dev/prod

### Обработка паролей

- Пароли используются только для привязки аккаунта
- Сообщения с паролями автоматически удаляются
- Пароли не сохраняются в боте

### Аутентификация запросов

- Все запросы к API включают `X-Telegram-Chat-ID` header
- Backend проверяет, что chat_id принадлежит пользователю
- Используется JWT токен для защищённых операций

## Мониторинг и логирование

### Просмотр логов

```bash
# Docker
docker-compose logs -f telegram_bot

# Локально
# Логи выводятся в stdout
```

### Уровни логирования

- `DEBUG` - детальная информация (только для разработки)
- `INFO` - основные события (команды, действия)
- `WARNING` - предупреждения
- `ERROR` - ошибки

### Метрики

Рекомендуется отслеживать:
- Количество активных пользователей
- Частота использования команд
- Ошибки при обработке запросов
- Время ответа API

## Troubleshooting

### Бот не отвечает

1. Проверьте, что бот запущен:
   ```bash
   docker-compose ps telegram_bot
   ```

2. Проверьте логи:
   ```bash
   docker-compose logs telegram_bot
   ```

3. Проверьте токен в `.env`

### Ошибки при привязке аккаунта

1. Проверьте, что backend API доступен
2. Проверьте правильность email/пароля
3. Проверьте, что пользователь активирован

### Не приходят уведомления

1. Проверьте настройки уведомлений: `/notifications`
2. Проверьте, что telegram_chat_id сохранён в БД
3. Проверьте логи backend на наличие ошибок отправки

## Roadmap

Планируемые улучшения:

- [ ] Поддержка групповых чатов
- [ ] Расширенные фильтры поиска
- [ ] Экспорт данных в различных форматах
- [ ] Голосовые команды
- [ ] Интеграция с Telegram Payments
- [ ] Статистика использования бота
- [ ] A/B тестирование интерфейса

## Поддержка

При возникновении проблем:
1. Проверьте документацию
2. Изучите логи
3. Создайте issue в репозитории
4. Обратитесь к команде разработки
