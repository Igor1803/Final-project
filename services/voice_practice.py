import os
from aiogram import types
from config import AUDIO_PATH
import random
import speech_recognition as sr
from pydub import AudioSegment

# Пример эталонных фраз на русском
PHRASES = [
    {"file": "privet_ru.mp3", "text": "Привет! Как дела?", "keywords": ["привет", "как", "дела"]},
    {"file": "pogoda_ru.mp3", "text": "Какая сегодня погода?", "keywords": ["погода", "сегодня"]}
]

def get_random_phrase():
    return random.choice(PHRASES)

async def send_practice_phrase(message: types.Message):
    phrase = get_random_phrase()
    audio_path = os.path.join(AUDIO_PATH, phrase["file"])
    if os.path.exists(audio_path):
        with open(audio_path, "rb") as audio:
            await message.answer_voice(audio, caption=phrase["text"])
    else:
        await message.answer(f"[Аудиофайл не найден: {phrase['file']}]. Текст: {phrase['text']}")
    return phrase

async def recognize_and_check(audio_file_path, phrase):
    # Конвертация ogg в wav для SpeechRecognition
    wav_path = audio_file_path.replace('.ogg', '.wav')
    AudioSegment.from_file(audio_file_path).export(wav_path, format='wav')
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio, language='ru-RU')
    except Exception as e:
        recognized_text = ''
    if os.path.exists(wav_path):
        os.remove(wav_path)
    # Проверка по ключевым словам
    if all(kw.lower() in recognized_text.lower() for kw in phrase["keywords"]):
        return True, recognized_text
    return False, recognized_text 