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

# Бот будет хранить список всех чатов, куда его добавили как админа
# Но для начала, так как у нас нет БД для групп, бот будет пытаться публиковать
# везде, где он есть в списке администраторов (или просто рассылать).
# Однако для стабильности лучше вести список групп.

async def forward_to_all_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка, что сообщение получено от пользователя
    if not update.effective_user:
        return

    # Проверка отправителя
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    # Целевые каналы из переменных окружения
    target_channels = os.getenv("TARGET_CHANNELS", "").split(",")
    
    for channel_id in target_channels:
        channel_id = channel_id.strip()
        if not channel_id:
            continue
        try:
            await context.bot.copy_message(
                chat_id=channel_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except Exception as e:
            logging.error(f"Не удалось отправить в {channel_id}: {e}")



if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Слушаем все типы сообщений, кроме команд
    handler = MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_all_channels)
    application.add_handler(handler)
    
    application.run_polling()
