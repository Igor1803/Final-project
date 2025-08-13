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

def handle_support_message(user_question: str):
    """Обработка сообщения поддержки"""
    try:
        answer = find_faq_answer(user_question)
        if answer:
            return answer, False  # Ответ найден, оператор не нужен
        else:
            return "Извините, я не нашел ответ на ваш вопрос. Перевожу вас к оператору.", True  # Нужен оператор
    except Exception as e:
        print(f"Ошибка обработки поддержки: {e}")
        return "Произошла ошибка. Перевожу вас к оператору.", True 