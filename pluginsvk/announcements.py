from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from dnevnik import get_announcements

db = SQLighter('db.db')
bp = Blueprint('announcements')

async def announcements(event):
	account_id = db.get_account_id(get_uid(event.object.user_id))
	account = db.get_account(account_id)
	result = await get_announcements(account[1], account[2], account[3], account[4])
	await bp.api.messages.send(event.object.user_id, 0, message=result)