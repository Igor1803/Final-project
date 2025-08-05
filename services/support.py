import json
from config import FAQ_PATH

# Загрузка базы FAQ
with open(FAQ_PATH, encoding='utf-8') as f:
    FAQ = json.load(f)

def find_faq_answer(user_question: str):
    user_question = user_question.lower()
    for item in FAQ:
        if item['question'].lower() in user_question or user_question in item['question'].lower():
            return item['answer']
    return None

def need_operator(user_question: str):
    # Если нет ответа в FAQ — нужен оператор
    return find_faq_answer(user_question) is None 