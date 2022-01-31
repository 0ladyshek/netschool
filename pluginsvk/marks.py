from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from dnevnik import get_marks
from .keyboard import keyboard_marks

db = SQLighter('db.db')
bp = Blueprint('marks')

async def marks(event):
	account_id = db.get_account_id(get_uid(event.object.user_id))
	account = db.get_account(account_id)
	result = await get_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bp.api.messages.send(event.object.user_id, 0, message=result[x:x+4096])
			await bp.api.messages.send(user_id=event.object.user_id, message='✅Все!', keyboard=keyboard_marks) 
	else:
		await bp.api.messages.send(event.object.user_id, 0, message=result, keyboard=keyboard_marks)