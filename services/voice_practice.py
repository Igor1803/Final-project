"""
Сервис для работы с голосовой практикой
"""
import os
import re
from difflib import SequenceMatcher
from services.fallback_voice_processor import FallbackVoiceProcessor

# База фраз для практики
PHRASES = [
    {
        "file": "privet_ru.mp3", 
        "text": "Привет! Как дела?", 
        "keywords": ["привет", "как", "дела"], 
        "expected_responses": ["привет", "здравствуйте", "хорошо", "нормально", "отлично"]
    },
    {
        "file": "pogoda_ru.mp3", 
        "text": "Какая сегодня погода?", 
        "keywords": ["погода", "сегодня"], 
        "expected_responses": ["хорошая", "плохая", "солнечно", "дождливо", "тепло", "холодно"]
    },
    {
        "file": "hello.mp3", 
        "text": "Привет! Как тебя зовут?", 
        "keywords": ["привет", "зовут", "имя"], 
        "expected_responses": ["меня зовут", "я", "мое имя"]
    },
    {
        "file": "name.mp3", 
        "text": "Расскажи о себе", 
        "keywords": ["расскажи", "себе"], 
        "expected_responses": ["я", "меня", "мне", "живу", "работаю", "учусь"]
    },
    {
        "file": "city.mp3", 
        "text": "Из какого ты города?", 
        "keywords": ["город", "откуда"], 
        "expected_responses": ["из", "живу в", "город", "москва", "спб", "питер"]
    },
    {
        "file": "job.mp3", 
        "text": "Кем ты работаешь?", 
        "keywords": ["работаешь", "профессия"], 
        "expected_responses": ["работаю", "я", "программист", "учитель", "студент"]
    },
    {
        "file": "hobby.mp3", 
        "text": "Какие у тебя хобби?", 
        "keywords": ["хобби", "увлечения"], 
        "expected_responses": ["люблю", "нравится", "хобби", "спорт", "музыка", "книги"]
    }
]

def normalize_text(text):
    """Нормализация текста для сравнения"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text

def calculate_similarity(text1, text2):
    """Вычисление схожести между двумя текстами"""
    return SequenceMatcher(None, text1, text2).ratio()

def check_response_quality(recognized_text, phrase):
    """Проверка качества ответа пользователя"""
    normalized_recognized = normalize_text(recognized_text)
    
    # Проверка по ключевым словам
    keywords_found = 0
    for keyword in phrase["keywords"]:
        if keyword.lower() in normalized_recognized:
            keywords_found += 1
    
    keywords_score = keywords_found / len(phrase["keywords"])
    
    # Проверка по ожидаемым ответам
    best_similarity = 0
    for expected in phrase.get("expected_responses", []):
        similarity = calculate_similarity(normalized_recognized, normalize_text(expected))
        best_similarity = max(best_similarity, similarity)
    
    # Бонус за ключевые слова
    if keywords_score > 0:
        keywords_score = min(1.0, keywords_score + 0.2)
    
    # Бонус за длину ответа
    length_bonus = 0.1 if len(normalized_recognized.split()) >= 2 else 0
    
    # Общая оценка
    total_score = (keywords_score + best_similarity) / 2 + length_bonus
    
    return {
        "score": total_score,
        "keywords_score": keywords_score,
        "similarity_score": best_similarity,
        "is_good": total_score > 0.3
    }

async def recognize_and_check(audio_file_path, phrase):
    """Распознавание речи и проверка ответа"""
    try:
        print(f"🎤 Обработка голосового сообщения: {audio_file_path}")
        
        # Используем резервный процессор
        recognized_text, error = FallbackVoiceProcessor.process_voice_message(audio_file_path)
        
        if error:
            print(f"❌ Ошибка обработки: {error}")
            return False, "", f"Ошибка обработки аудио: {error}"
        
        if not recognized_text:
            print("❌ Речь не распознана")
            return False, "", "Не удалось распознать речь. Попробуйте говорить четче и громче."
        
        print(f"✅ Распознано: '{recognized_text}'")
        
        # Проверка качества ответа
        quality = check_response_quality(recognized_text, phrase)
        
        if quality["is_good"]:
            feedback = f"✅ Отлично! Вы сказали: '{recognized_text}'"
            result = True, recognized_text, feedback
        else:
            feedback = f"🔄 Попробуйте еще раз. Вы сказали: '{recognized_text}'\n"
            if quality["keywords_score"] < 0.5:
                feedback += "💡 Совет: используйте ключевые слова из вопроса."
            elif quality["similarity_score"] < 0.3:
                feedback += "💡 Совет: ответ должен быть более похож на ожидаемый."
            result = False, recognized_text, feedback
        
        return result
            
    except Exception as e:
        print(f"❌ Общая ошибка в recognize_and_check: {e}")
        return False, "", f"Произошла ошибка при обработке аудио: {str(e)}"

def get_phrase_by_file(filename):
    """Получение фразы по имени файла"""
    for phrase in PHRASES:
        if phrase["file"] == filename:
            return phrase
    return None
