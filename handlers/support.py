from aiogram import Router
from aiogram.types import Message
from services.support import find_faq_answer, need_operator
from config import OPERATOR_ID
from services.logger import log_dialog, log_error

router = Router()

@router.message(lambda m: 'оператор' in m.text.lower())
async def handle_operator_request(message: Message):
    try:
        await message.bot.send_message(OPERATOR_ID, f'Новый запрос от пользователя {message.from_user.id}:\n{message.text}')
        response = 'Ваш запрос передан оператору. Ожидайте ответа.'
        await message.answer(response)
        log_dialog(message.from_user.id, message.text, response)
    except Exception as e:
        log_error(f"Operator error: {e}")
        await message.answer('Произошла ошибка при передаче оператору.')

@router.message()
async def handle_support(message: Message):
    try:
        user_question = message.text
        answer = find_faq_answer(user_question)
        if answer:
            await message.answer(answer)
            log_dialog(message.from_user.id, user_question, answer)
        else:
            response = 'Не могу найти ответ. Хотите связаться с оператором? Напишите "Оператор".'
            await message.answer(response)
            log_dialog(message.from_user.id, user_question, response)
    except Exception as e:
        log_error(f"Support error: {e}")
        await message.answer('Произошла ошибка при обработке запроса.') 