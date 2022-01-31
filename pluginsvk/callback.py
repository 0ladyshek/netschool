from vkbottle import GroupTypes, GroupEventType
from vkbottle.bot import Blueprint
from .importaccount import importaccount
from .registration import registration
from .menu import menu
from .cancel import cancel
from .date import date, action
from .delete import delete, yes_delete
from .info import info
from .exit import exit
from .overdue import overdue
from .announcements import announcements
from .marks import marks
from .detail_marks import detail_marks
from .birthdays import birthStaff, birthParent, birthStudent, birthYear, birthDay

bp = Blueprint('callback')

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, GroupTypes.MessageEvent)
async def _(event: GroupTypes.MessageEvent):
	for keys in event.object.payload:
		key = keys 
	if key == 'cmd':
		if event.object.payload[key] == 'import_account':
			await importaccount(event)
		elif event.object.payload[key] == 'new_account':
			await registration(event)
		elif event.object.payload[key] == 'cancel':
			await cancel(event)
	elif key == 'account':
		await menu(event)
	elif key == 'dnevnik':
		if event.object.payload[key] == 'rasp' or event.object.payload[key] == 'dz':
			await date(event)
		elif event.object.payload[key] == 'delete':
			await delete(event)
		elif event.object.payload[key] == 'info':
			await info(event)
		elif event.object.payload[key] == 'exit':
			await exit(event)
		elif event.object.payload[key] == 'overdue':
			await overdue(event)
		elif event.object.payload[key] == 'announcements':
			await announcements(event)
		elif event.object.payload[key] == 'marks':
			await marks(event)
		elif event.object.payload[key] == 'detail_mark':
			await detail_marks(event)
		elif event.object.payload[key] == 'birthDays':
			await birthDay(event)
		elif event.object.payload[key] == 'birthStaff':
			await birthStaff(event)
		elif event.object.payload[key] == 'birthParent':
			await birthParent(event)
		elif event.object.payload[key] == 'birthStudent':
			await birthStudent(event)
		elif event.object.payload[key] == 'birthYear':
			await birthYear(event)
	elif key == 'date':
		await action(event)
	elif key == 'delete':
		await yes_delete(event)