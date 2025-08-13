from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ContentType
from services.voice_practice import recognize_and_check, PHRASES, get_phrase_by_file
import os
from services.logger import log_dialog, log_error
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class PracticeState(StatesGroup):
    waiting_for_response = State()

# Словарь для хранения текущих фраз для каждого пользователя
user_current_phrases = {}

@router.message(lambda m: m.content_type == ContentType.VOICE)
async def handle_voice(message: Message, state: FSMContext):
    try:
        print(f"🎤 Получено голосовое сообщение от пользователя {message.from_user.id}")
        
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        file_path = file.file_path
        local_path = f"temp_{voice.file_id}.ogg"
        
        print(f"📥 Скачивание файла: {local_path}")
        await message.bot.download_file(file_path, local_path)
        
        # Проверяем, что файл скачался
        if not os.path.exists(local_path):
            await message.answer("❌ Ошибка: не удалось скачать аудиофайл")
            return
        
        print(f"✅ Файл скачан: {local_path} ({os.path.getsize(local_path)} байт)")
        
        # Получаем текущую фразу пользователя
        current_state = await state.get_state()
        if current_state == PracticeState.waiting_for_response.state:
            # Пользователь в режиме практики
            user_data = await state.get_data()
            current_phrase = user_data.get('current_phrase')
            
            if current_phrase:
                print(f"🎯 Обработка в режиме практики: {current_phrase['text']}")
                try:
                    ok, recognized, feedback = await recognize_and_check(local_path, current_phrase)
                    await message.answer(feedback)
                    
                    if ok:
                        # Переходим к следующей фразе или завершаем практику
                        await send_next_phrase(message, state)
                    else:
                        # Повторяем ту же фразу
                        await repeat_current_phrase(message, state)
                except Exception as e:
                    print(f"❌ Ошибка в режиме практики: {e}")
                    await message.answer("Произошла ошибка при обработке голосового сообщения. Попробуйте еще раз или начните практику заново командой /practice.")
            else:
                await message.answer("Начните практику командой /practice")
        else:
            # Обычный режим - проверяем с первой фразой
            print("🔍 Обычный режим - тестирование с первой фразой")
            try:
                phrase = PHRASES[0]
                ok, recognized, feedback = await recognize_and_check(local_path, phrase)
                await message.answer(feedback)
                
                if ok:
                    await message.answer("Отлично! Теперь попробуйте команду /practice для полноценной практики.")
            except Exception as e:
                print(f"❌ Ошибка в обычном режиме: {e}")
                await message.answer("Произошла ошибка при обработке голосового сообщения. Попробуйте еще раз или обратитесь в поддержку.")
        
        log_dialog(message.from_user.id, '[voice]', f"Recognized: {recognized if 'recognized' in locals() else 'error'}")
        
    except Exception as e:
        print(f"❌ Ошибка обработки голоса: {e}")
        log_error(f"Voice error: {e}")
        await message.answer('Произошла ошибка при обработке голосового сообщения.')
    finally:
        # Очистка временного файла
        if 'local_path' in locals() and os.path.exists(local_path):
            try:
                os.remove(local_path)
                print(f"🧹 Удален временный файл: {local_path}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить временный файл: {e}")

async def send_next_phrase(message: Message, state: FSMContext):
    """Отправка следующей фразы в практике"""
    user_data = await state.get_data()
    current_index = user_data.get('phrase_index', -1)
    next_index = current_index + 1
    
    if next_index < len(PHRASES):
        # Отправляем следующую фразу
        phrase = PHRASES[next_index]
        audio_path = os.path.join("audio", phrase["file"])
        
        if os.path.exists(audio_path):
            try:
                from aiogram.types import FSInputFile
                voice = FSInputFile(audio_path)
                await message.answer_voice(voice, caption=f"📝 {phrase['text']}\n\n🎤 Ответьте голосом на этот вопрос")
            except Exception as e:
                print(f"❌ Ошибка отправки голосового сообщения: {e}")
                await message.answer(f"📝 {phrase['text']}\n\n🎤 Ответьте голосом на этот вопрос")
        else:
            await message.answer(f"❌ Аудиофайл не найден: {phrase['file']}\n\n📝 {phrase['text']}")
        
        # Обновляем состояние
        await state.update_data(
            current_phrase=phrase,
            phrase_index=next_index
        )
        await state.set_state(PracticeState.waiting_for_response)
    else:
        # Практика завершена
        await message.answer("🎉 Поздравляем! Вы завершили практику!\n\nИспользуйте /practice для новой сессии.")
        await state.clear()

async def repeat_current_phrase(message: Message, state: FSMContext):
    """Повторение текущей фразы"""
    user_data = await state.get_data()
    current_phrase = user_data.get('current_phrase')
    
    if current_phrase:
        audio_path = os.path.join("audio", current_phrase["file"])
        
        if os.path.exists(audio_path):
            try:
                from aiogram.types import FSInputFile
                voice = FSInputFile(audio_path)
                await message.answer_voice(voice, caption=f"🔄 Попробуйте еще раз:\n📝 {current_phrase['text']}")
            except Exception as e:
                print(f"❌ Ошибка отправки голосового сообщения: {e}")
                await message.answer(f"🔄 Попробуйте еще раз:\n📝 {current_phrase['text']}")
        else:
            await message.answer(f"🔄 Попробуйте еще раз:\n📝 {current_phrase['text']}") 