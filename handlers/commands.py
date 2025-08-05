from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from services.voice_practice import send_practice_phrase
from services.logger import log_dialog, log_error

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    try:
        response = 'Привет! Я SpeakSmart — бот для языковой практики и поддержки.\nИспользуйте /practice для тренировки или /support для связи с поддержкой.'
        await message.answer(response)
        log_dialog(message.from_user.id, '/start', response)
    except Exception as e:
        log_error(f"Start error: {e}")
        await message.answer('Произошла ошибка.')

@router.message(Command("help"))
async def cmd_help(message: Message):
    try:
        response = 'Доступные команды:\n/start — начать\n/practice — языковая практика\n/support — поддержка'
        await message.answer(response)
        log_dialog(message.from_user.id, '/help', response)
    except Exception as e:
        log_error(f"Help error: {e}")
        await message.answer('Произошла ошибка.')

@router.message(Command("practice"))
async def cmd_practice(message: Message):
    try:
        response = 'Языковая практика: сейчас отправлю голосовую фразу...'
        await message.answer(response)
        phrase = await send_practice_phrase(message)
        log_dialog(message.from_user.id, '/practice', response + f' [{phrase["text"]}]')
        # TODO: интеграция с FSM/state
    except Exception as e:
        log_error(f"Practice error: {e}")
        await message.answer('Произошла ошибка.')

@router.message(Command("support"))
async def cmd_support(message: Message):
    try:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text='Частые вопросы')],
            [KeyboardButton(text='Связаться с оператором')]
        ])
        response = 'Выберите вопрос или напишите свой:'
        await message.answer(response, reply_markup=kb)
        log_dialog(message.from_user.id, '/support', response)
    except Exception as e:
        log_error(f"SupportCmd error: {e}")
        await message.answer('Произошла ошибка.') 