from aiogram import Router, types, F
from config import OPERATOR_ID

router = Router()

@router.message(F.text.casefold() == "оператор")
async def send_to_operator(message: types.Message):
    """
    Обработчик запроса к оператору.
    Если пользователь вводит слово 'Оператор',
    бот отправляет уведомление и пересылает запрос оператору.
    """
    try:
        # Уведомляем пользователя
        await message.answer("Передаю ваш запрос оператору...")

        # Формируем текст для оператора
        user_info = f"📩 Запрос от пользователя:\nID: {message.from_user.id}\n"
        if message.from_user.username:
            user_info += f"Username: @{message.from_user.username}\n"
        if message.from_user.full_name:
            user_info += f"Имя: {message.from_user.full_name}\n"
        user_info += f"\nСообщение: {message.text}"

        # Отправляем оператору
        await message.bot.send_message(OPERATOR_ID, user_info)

        # Пересылаем сообщение, на которое был дан ответ (если есть)
        if message.reply_to_message:
            await message.bot.forward_message(
                OPERATOR_ID,
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )

    except Exception as e:
        await message.answer(f"⚠ Ошибка при передаче оператору: {e}")
