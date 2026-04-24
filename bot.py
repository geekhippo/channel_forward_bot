import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

logging.basicConfig(level=logging.INFO)

async def forward_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка отправителя
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    # Копируем сообщение в канал от имени бота
    await context.bot.copy_message(
        chat_id=TARGET_CHANNEL_ID,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Слушаем все типы сообщений, кроме команд
    handler = MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_channel)
    application.add_handler(handler)
    
    application.run_polling()
