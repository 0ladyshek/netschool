from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from .keyboard import keyboard_delete, accounts, keyboard_clean
from .state import MenuState

db = SQLighter('db.db')
bp = Blueprint('delete')

async def delete(event):
	await bp.state_dispenser.set(event.object.user_id, MenuState.DELETE)
	await bp.api.messages.send(event.object.user_id, 0, message='⚠️Потвердите что Вы в здравом уме и светлой памяти согласны на удаление аккаунта', keyboard=keyboard_delete)

async def yes_delete(event):
	db.delete_account(db.get_account_id(get_uid(event.object.user_id)), get_uid(event.object.user_id))
	keyboard = await accounts(get_uid(event.object.user_id))
	await bp.state_dispenser.delete(event.object.user_id)
	await bp.api.messages.send(event.object.user_id, 0, message='✅Удалил аккаунт', keyboard=keyboard_clean)
	await bp.api.messages.send(event.object.user_id, 0, message='📜Выбери аккаунт из списка ниже или создай новый', keyboard=keyboard)