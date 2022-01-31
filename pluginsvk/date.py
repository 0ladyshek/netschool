from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
import datetime
from dnevnik import get_rasp, get_dz
from .keyboard import keyboard_date
from .state import MenuState

db = SQLighter('db.db')
bp = Blueprint('date')

async def date(event):
	if event.object.payload['dnevnik'] == 'rasp':
		await bp.state_dispenser.set(event.object.user_id, MenuState.RASP)
	elif event.object.payload['dnevnik'] == 'dz':
		await bp.state_dispenser.set(event.object.user_id, MenuState.DZ)
	await bp.api.messages.send(event.object.user_id, 0, message='🗓Выберите дату', keyboard=keyboard_date)

async def action(event):
	account = db.get_account(db.get_account_id(get_uid(event.object.user_id)))
	state = await bp.state_dispenser.get(event.object.user_id)
	if event.object.payload['date'] == 'yesterday':
		start = end = datetime.date.today() + datetime.timedelta(days=-1)
	elif event.object.payload['date'] == 'today':
		start = end = datetime.date.today()
	elif event.object.payload['date'] == 'tomorrow':
		start = end = datetime.date.today() + datetime.timedelta(days=1)
	elif event.object.payload['date'] == 'week':
		start = end = None
	if state.state == 1:
		result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	elif state.state == 2:
		result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bp.api.messages.send(event.object.user_id, 0, message=result[x:x+4096])
		await bp.api.messages.send(event.object.user_id, 0, message='✅Все!')
	else:
		await bp.api.messages.send(event.object.user_id, 0, message=result)