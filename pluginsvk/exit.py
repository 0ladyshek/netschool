from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from .keyboard import accounts, keyboard_clean

db = SQLighter('db.db')
bp = Blueprint('exit')

async def exit(event):
	db.edit_account_id(0, get_uid(event.object.user_id))
	keyboard = await accounts(get_uid(event.object.user_id))
	await bp.api.messages.send(event.object.user_id, 0, message='✅Вышел из аккаунта', keyboard=keyboard_clean)
	await bp.api.messages.send(event.object.user_id, 0, message='📜Выбери аккаунт из списка ниже или создай новый', keyboard=keyboard)