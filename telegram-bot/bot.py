"""
Tender Platform - Telegram Bot
Production-grade Telegram bot for tender notifications and user interactions.
"""

import os
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from pydantic_settings import BaseSettings


# ============================================================================
# CONFIGURATION
# ============================================================================
class BotSettings(BaseSettings):
    """Bot configuration from environment variables."""
    
    TELEGRAM_BOT_TOKEN: str = ""
    BACKEND_API_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = BotSettings()

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
)
logger = logging.getLogger(__name__)


# ============================================================================
# BOT STATE & STORAGE
# ============================================================================
class UserState:
    """Simple in-memory user state storage."""
    
    def __init__(self):
        self._states: dict[int, dict] = {}
    
    def get(self, user_id: int) -> dict:
        return self._states.get(user_id, {})
    
    def set(self, user_id: int, state: dict):
        self._states[user_id] = state
    
    def delete(self, user_id: int):
        self._states.pop(user_id, None)


user_state = UserState()


# ============================================================================
# COMMAND HANDLERS
# ============================================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я бот платформы тендеров Tender Platform.\n\n"
        "Доступные команды:\n"
        "/help - Показать справку\n"
        "/tenders - Последние тендеры\n"
        "/subscribe - Подписаться на уведомления\n"
        "/unsubscribe - Отписаться от уведомлений\n"
        "/profile - Мой профиль\n"
        "/settings - Настройки уведомлений\n\n"
        "Нажмите /help для подробной информации."
    )
    
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "📚 **Справка по боту Tender Platform**\n\n"
        "**Основные команды:**\n"
        "/start - Запустить бота\n"
        "/help - Эта справка\n\n"
        "**Тендеры:**\n"
        "/tenders - Последние тендеры\n"
        "/search <запрос> - Поиск тендеров\n"
        "/tender <номер> - Информация о тендере\n\n"
        "**Уведомления:**\n"
        "/subscribe - Подписаться на уведомления\n"
        "/unsubscribe - Отписаться\n"
        "/settings - Настроить фильтры\n\n"
        "**Профиль:**\n"
        "/profile - Информация о профиле\n"
        "/favorites - Избранные тендеры\n\n"
        "**Поддержка:**\n"
        "По вопросам обращайтесь: support@tender-platform.com"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Последние тендеры", callback_data="tenders")],
        [InlineKeyboardButton("🔔 Подписаться", callback_data="subscribe")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)


async def tenders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tenders command - show latest tenders."""
    await update.message.reply_text(
        "📋 **Последние тендеры**\n\n"
        "Загрузка списка тендеров...\n\n"
        "_Примечание: Для получения данных необходимо подключение к API._"
    )
    
    # In production, fetch from backend API
    # Example: GET {BACKEND_API_URL}{API_V1_PREFIX}/tenders?limit=5
    sample_tenders = [
        {
            "number": "Т-2024-001",
            "title": "Поставка офисного оборудования",
            "price": "1 500 000 ₽",
            "deadline": "2024-02-15",
        },
        {
            "number": "Т-2024-002",
            "title": "Услуги по уборке помещений",
            "price": "800 000 ₽",
            "deadline": "2024-02-20",
        },
    ]
    
    for tender in sample_tenders:
        text = (
            f"📄 **{tender['number']}**\n"
            f"{tender['title']}\n\n"
            f"💰 Начальная цена: {tender['price']}\n"
            f"⏰ До подачи: {tender['deadline']}\n"
        )
        keyboard = [[InlineKeyboardButton("Подробнее", callback_data=f"tender_{tender['number']}")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subscribe command."""
    user_id = update.effective_user.id
    
    # Store user subscription state
    user_state.set(user_id, {"subscribed": True, "filters": {}})
    
    await update.message.reply_text(
        "✅ **Вы успешно подписаны на уведомления!**\n\n"
        "Теперь вы будете получать уведомления о:\n"
        "• Новых тендерах по вашим фильтрам\n"
        "• Изменениях статуса тендеров\n"
        "• Приближающихся дедлайнах\n\n"
        "Используйте /settings для настройки фильтров."
    )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unsubscribe command."""
    user_id = update.effective_user.id
    user_state.delete(user_id)
    
    await update.message.reply_text(
        "❌ **Вы отписались от уведомлений.**\n\n"
        "Используйте /subscribe чтобы подписаться снова."
    )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command."""
    user = update.effective_user
    state = user_state.get(user.id)
    
    subscribed = "✅ Да" if state.get("subscribed") else "❌ Нет"
    
    profile_text = (
        f"👤 **Ваш профиль**\n\n"
        f"Telegram ID: `{user.id}`\n"
        f"Имя: {user.first_name} {user.last_name or ''}\n"
        f"Username: @{user.username or 'не указан'}\n\n"
        f"🔔 Подписка на уведомления: {subscribed}\n"
    )
    
    await update.message.reply_text(profile_text)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command."""
    keyboard = [
        [InlineKeyboardButton("💰 Диапазон цен", callback_data="setting_price")],
        [InlineKeyboardButton("📍 Регионы", callback_data="setting_region")],
        [InlineKeyboardButton("📂 Категории", callback_data="setting_category")],
        [InlineKeyboardButton("⏰ Дедлайны", callback_data="setting_deadline")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ **Настройки уведомлений**\n\n"
        "Выберите параметр для настройки:",
        reply_markup=reply_markup
    )


# ============================================================================
# CALLBACK QUERY HANDLER
# ============================================================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "tenders":
        await tenders_command(update, context)
    elif data == "subscribe":
        await subscribe_command(update, context)
    elif data == "settings":
        await settings_command(update, context)
    elif data.startswith("tender_"):
        tender_number = data.replace("tender_", "")
        await query.edit_message_text(
            f"📄 **Тендер {tender_number}**\n\n"
            f"Подробная информация о тендере...\n"
            f"_В реальной версии данные загружаются из API_"
        )
    elif data.startswith("setting_"):
        setting_type = data.replace("setting_", "")
        await query.edit_message_text(
            f"⚙️ Настройка: **{setting_type}**\n\n"
            f"Функционал в разработке..."
        )


# ============================================================================
# MESSAGE HANDLER
# ============================================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    text = update.message.text.lower()
    
    if "тендер" in text or "закупк" in text:
        await update.message.reply_text(
            "🔍 Для поиска тендеров используйте команду /search <запрос>\n"
            "Или посмотрите все тендеры: /tenders"
        )
    else:
        await update.message.reply_text(
            "Я не понял ваш запрос. Используйте /help для просмотра доступных команд."
        )


# ============================================================================
# ERROR HANDLER
# ============================================================================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😕 Произошла ошибка при обработке вашего запроса.\n"
            "Пожалуйста, попробуйте позже."
        )


# ============================================================================
# APPLICATION FACTORY
# ============================================================================
def create_application() -> Application:
    """Create and configure the Telegram bot application."""
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set. Bot will not start.")
        return None
    
    # Build application
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .build()
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tenders", tenders_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    return application


# ============================================================================
# MAIN
# ============================================================================
async def main() -> None:
    """Main entry point."""
    logger.info("Starting Tender Platform Telegram Bot...")
    
    app = create_application()
    
    if app:
        logger.info("Bot initialized successfully")
        # Start polling
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
    else:
        logger.error("Failed to initialize bot. Check TELEGRAM_BOT_TOKEN.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
