# handlers/practice_handler.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os
from aiogram.types import FSInputFile
from services.voice_practice import PHRASES
from aiogram.fsm.state import State, StatesGroup

router = Router()

class PracticeState(StatesGroup):
    waiting_for_response = State()

@router.message(Command("practice"))
async def practice_session(message: types.Message, state: FSMContext):
    """Начало сессии практики"""
    await message.answer("🎯 Начинаем практику разговорного русского языка!")
    await message.answer("📋 Правила:\n"
                        "• Я буду задавать вопросы голосом\n"
                        "• Вы отвечайте голосом\n"
                        "• Я проверю ваш ответ и дам обратную связь\n"
                        "• При правильном ответе переходим к следующему вопросу\n\n"
                        "🚀 Готовы? Начинаем!")
    
    # Начинаем с первой фразы
    await send_first_phrase(message, state)

@router.message(Command("stop_practice"))
async def stop_practice(message: types.Message, state: FSMContext):
    """Остановка практики"""
    await state.clear()
    await message.answer("⏹ Практика остановлена. Используйте /practice для новой сессии.")

@router.message(Command("help_practice"))
async def help_practice(message: types.Message):
    """Справка по практике"""
    help_text = """
🎯 **Практика разговорного русского языка**

**Команды:**
/practice - Начать практику
/stop_practice - Остановить практику
/help_practice - Эта справка

**Как это работает:**
1. Бот задает вопрос голосом
2. Вы отвечаете голосовым сообщением
3. Бот распознает вашу речь и сравнивает с эталоном
4. Вы получаете обратную связь и рекомендации

**Советы для лучшего распознавания:**
• Говорите четко и не спеша
• Используйте ключевые слова из вопроса
• Старайтесь отвечать по существу
• Избегайте фонового шума

**Темы практики:**
• Приветствие и знакомство
• Рассказ о себе
• Город и место жительства
• Работа и профессия
• Хобби и увлечения
• Погода и повседневные темы
"""
    await message.answer(help_text)

async def send_first_phrase(message: types.Message, state: FSMContext):
    """Отправка первой фразы практики"""
    if PHRASES:
        # Проверяем, есть ли уже сохраненный индекс
        user_data = await state.get_data()
        phrase_index = user_data.get('phrase_index', 0)
        
        # Если индекс больше количества фраз, начинаем сначала
        if phrase_index >= len(PHRASES):
            phrase_index = 0
        
        phrase = PHRASES[phrase_index]
        audio_path = os.path.join("audio", phrase["file"])
        
        if os.path.exists(audio_path):
            try:
                voice = FSInputFile(audio_path)
                await message.answer_voice(
                    voice, 
                    caption=f"📝 **Вопрос:** {phrase['text']}\n\n🎤 **Ответьте голосом на этот вопрос**"
                )
            except Exception as e:
                print(f"❌ Ошибка отправки голосового сообщения: {e}")
                await message.answer(f"📝 **Вопрос:** {phrase['text']}\n\n🎤 **Ответьте голосом на этот вопрос**")
        else:
            await message.answer(f"❌ Аудиофайл не найден: {phrase['file']}\n\n📝 {phrase['text']}")
        
        # Устанавливаем состояние
        await state.update_data(
            current_phrase=phrase,
            phrase_index=phrase_index
        )
        await state.set_state(PracticeState.waiting_for_response)
    else:
        await message.answer("❌ Нет доступных фраз для практики.")
