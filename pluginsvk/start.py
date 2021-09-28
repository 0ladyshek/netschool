from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from tools import get_uid
from .keyboard import accounts

db = SQLighter('db.db')
bp = Blueprint('start')

@bp.on.private_message(text="Начать")
async def _(message: Message):
    if not db.user_exists(user_id=get_uid(message.from_id)):
        db.add_user(get_uid(message.from_id))
    keyboard = await accounts(get_uid(message.from_id))
    await message.answer('📜Выбери аккаунт из списка ниже или создай новый', keyboard = keyboard)