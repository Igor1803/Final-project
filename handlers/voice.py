from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ContentType
from services.voice_practice import recognize_and_check, PHRASES
import os
from services.logger import log_dialog, log_error

router = Router()

@router.message(lambda m: m.content_type == ContentType.VOICE)
async def handle_voice(message: Message):
    try:
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        file_path = file.file_path
        local_path = f"temp_{voice.file_id}.ogg"
        await message.bot.download_file(file_path, local_path)
        phrase = PHRASES[0]  # Для теста — первая фраза
        ok, recognized = await recognize_and_check(local_path, phrase)
        if ok:
            response = f"Правильно! Вы сказали: {recognized}"
        else:
            response = f"Попробуйте ещё раз. Я услышал: {recognized}"
        await message.answer(response)
        log_dialog(message.from_user.id, '[voice]', response)
        os.remove(local_path)
    except Exception as e:
        log_error(f"Voice error: {e}")
        await message.answer('Произошла ошибка при обработке голосового сообщения.') 