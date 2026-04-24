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
import asyncio

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHANNELS = os.getenv("TARGET_CHANNELS", "").split(",")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

logging.basicConfig(level=logging.INFO)

# Кэш для хранения медиа-групп (media_group_id -> [messages])
media_groups = {}

async def forward_to_all_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != ALLOWED_USER_ID:
        return

    msg = update.message
    
    if msg.media_group_id:
        if msg.media_group_id not in media_groups:
            media_groups[msg.media_group_id] = []
            # Ждем немного, пока придут все сообщения группы
            context.job_queue.run_once(send_media_group, 3, chat_id=update.effective_chat.id, data={'group_id': msg.media_group_id})
        
        media_groups[msg.media_group_id].append(msg)
        return

    # Если сообщение одиночное
    for channel_id in TARGET_CHANNELS:
        try:
            await context.bot.copy_message(chat_id=channel_id.strip(), from_chat_id=update.effective_chat.id, message_id=msg.message_id)
        except Exception as e:
            logging.error(f"Ошибка одиночного сообщения: {e}")

async def send_media_group(context: ContextTypes.DEFAULT_TYPE):
    group_id = context.job.data['group_id']
    messages = media_groups.pop(group_id, [])
    if not messages: return

    # Сортируем сообщения, чтобы порядок не нарушился
    messages.sort(key=lambda m: m.message_id)

    media = []
    for msg in messages:
        if msg.photo:
            media.append(InputMediaPhoto(media=msg.photo[-1].file_id, caption=msg.caption if msg.caption else None))
        elif msg.video:
            media.append(InputMediaVideo(media=msg.video.file_id, caption=msg.caption if msg.caption else None))
    
    for channel_id in TARGET_CHANNELS:
        try:
            await context.bot.send_media_group(chat_id=channel_id.strip(), media=media)
        except Exception as e:
            logging.error(f"Ошибка группы {channel_id}: {e}")





if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    
    # Слушаем все типы сообщений, кроме команд
    handler = MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_all_channels)
    application.add_handler(handler)
    
    application.run_polling()
