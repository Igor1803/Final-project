import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token_here')
OPERATOR_ID = int(os.getenv('OPERATOR_ID', '0'))  # ID оператора в Telegram

# Пути к файлам
AUDIO_PATH = 'audio/'
FAQ_PATH = 'data/faq.json'
DIALOGS_PATH = 'data/dialogs.json'
LOG_PATH = 'data/bot.log' 