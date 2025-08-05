import json
import datetime
from config import DIALOGS_PATH, LOG_PATH

# Сохраняет диалоговое событие
def log_dialog(user_id, user_message, bot_response):
    entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'user_id': user_id,
        'user_message': user_message,
        'bot_response': bot_response
    }
    try:
        with open(DIALOGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = []
    data.append(entry)
    with open(DIALOGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Логирует ошибку в текстовый лог
def log_error(error_text):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {error_text}\n") 