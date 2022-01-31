from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from .keyboard import keyboard_birthDays
from dnevnik import birthDays, birthYears

db = SQLighter('db.db')
bp = Blueprint('birthDays')

async def birthDay(event):
	await event.ctx_api.messages.send(user_id=event.object.user_id, message='📜Выберите кого вам показать', random_id=0, keyboard=keyboard_birthDays)

async def birthParent(event):
	account = db.get_account(db.get_account_id(get_uid(event.object.user_id)))
	result = await birthDays(account[1], account[2], account[3], account[4], parent = True)
	await event.ctx_api.messages.send(user_id=event.object.user_id, message=result, random_id=0)

async def birthStaff(event):
	account = db.get_account(db.get_account_id(get_uid(event.object.user_id)))
	result = await birthDays(account[1], account[2], account[3], account[4], staff = True)
	await event.ctx_api.messages.send(user_id=event.object.user_id, message=result, random_id=0)

async def birthStudent(event):
	account = db.get_account(db.get_account_id(get_uid(event.object.user_id)))
	result = await birthDays(account[1], account[2], account[3], account[4], student = True)
	await event.ctx_api.messages.send(user_id=event.object.user_id, message=result, random_id=0)

async def birthYear(event):
	account = db.get_account(db.get_account_id(get_uid(event.object.user_id)))
	result = await birthYears(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await event.ctx_api.messages.send(event.object.user_id, 0, message=result[x:x+4096])
		await event.ctx_api.messages.send(event.object.user_id, 0, message='✅Все!') 
	else:
		await event.ctx_api.messages.send(event.object.user_id, 0, message=result)