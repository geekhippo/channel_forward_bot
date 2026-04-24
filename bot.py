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

from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os
import logging
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHANNELS = os.getenv("TARGET_CHANNELS", "").split(",")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

logging.basicConfig(level=logging.INFO)

async def forward_to_all_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != ALLOWED_USER_ID:
        return

    msg = update.message
    
    # Если это альбом (медиа-группа)
    if msg.media_group_id:
        # Для простоты: группы сообщений в Telegram приходят как отдельные события, 
        # но мы можем подождать короткое время, чтобы собрать их все вместе.
        # Однако, текущая архитектура позволяет просто использовать copy_message 
        # для каждого элемента, если не критично сохранение альбома.
        # Если критично, нужно кэширование по media_group_id.
        pass

    for channel_id in TARGET_CHANNELS:
        channel_id = channel_id.strip()
        if not channel_id: continue
        try:
            # copy_message корректно переносит медиа-группы, если ID группы одинаковый
            await context.bot.copy_message(
                chat_id=channel_id,
                from_chat_id=update.effective_chat.id,
                message_id=msg.message_id
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке в {channel_id}: {e}")




if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Слушаем все типы сообщений, кроме команд
    handler = MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_all_channels)
    application.add_handler(handler)
    
    application.run_polling()
