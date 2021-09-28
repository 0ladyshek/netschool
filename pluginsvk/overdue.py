from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from dnevnik import get_overdue
import re

db = SQLighter('db.db')
bp = Blueprint('overdue')

async def overdue(event):
	account_id = db.get_account_id(get_uid(event.object.user_id))
	account = db.get_account(account_id)
	result = await get_overdue(account[1], account[2], account[3], account[4])
	resulttext= '🗒Просроченные задания:\n'
	for assignment in result:
		resulttext += f"{assignment['subjectName']}: {assignment['assignmentName']}(Дата сдачи: {re.search('(.*)T00:00:00', assignment['dueDate']).group(1)})\n"
	await bp.api.messages.send(event.object.user_id, 0, message=resulttext)