# services/faq_service.py
import json

def load_faq(path="data/faq.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки FAQ: {e}")
        return []

def find_answer(faq_data, user_question: str) -> str | None:
    user_question = user_question.lower()
    for item in faq_data:
        if item["question"].lower() in user_question:
            return item["answer"]
    return None

def get_faq_answer(user_question: str) -> str | None:
    """Получить ответ из FAQ по вопросу пользователя"""
    try:
        faq_data = load_faq()
        return find_answer(faq_data, user_question)
    except Exception as e:
        print(f"Ошибка поиска в FAQ: {e}")
        return None
