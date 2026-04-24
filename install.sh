#!/bin/bash

echo "🚀 Запуск установки @channel_forward_bot..."

# 1. Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Docker не найден. Устанавливаю..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi

# 2. Создание директории
mkdir -p channel_forward_bot
cd channel_forward_bot

# 3. Запрос данных
echo "📝 Нам понадобятся ваши ключи API."
read -p "Введите TELEGRAM_TOKEN: " TELEGRAM_TOKEN < /dev/tty
read -p "Введите список TARGET_CHANNEL_ID (через запятую, например -1001, -1002): " TARGET_CHANNELS < /dev/tty
read -p "Введите ALLOWED_USER_ID: " ALLOWED_USER_ID < /dev/tty

cat <<EOF > .env
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
TARGET_CHANNELS=$TARGET_CHANNELS
ALLOWED_USER_ID=$ALLOWED_USER_ID
EOF

# 4. Скачивание файлов
echo "📥 Скачиваю файлы бота..."
curl -sSL https://raw.githubusercontent.com/geekhippo/channel_forward_bot/master/bot.py -o bot.py
curl -sSL https://raw.githubusercontent.com/geekhippo/channel_forward_bot/master/Dockerfile -o Dockerfile
curl -sSL https://raw.githubusercontent.com/geekhippo/channel_forward_bot/master/requirements.txt -o requirements.txt

# 5. Сборка и запуск
echo "🏗️ Собираю и запускаю бота..."
docker build -t forward-bot .
docker stop forward-bot 2>/dev/null || true
docker rm forward-bot 2>/dev/null || true
docker run --name forward-bot --env-file .env -d --restart unless-stopped forward-bot

echo "🎉 Готово! Бот настроен на рассылку во все указанные каналы."
echo "Логи: docker logs -f forward-bot"
