from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from tools import get_uid
from typing import Optional
from .keyboard import keyboard_chat
import re

db = SQLighter('db.db')
bp = Blueprint('calls')
bp.labeler.ignore_case = True
bp.labeler.vbml_ignore_case = True
bp.labeler.vbml_flags = re.DOTALL

@bp.on.chat_message(payload={'chat': 'calls'})
async def _(message: Message):
	calls = db.get_calls(message.peer_id)
	if not calls:
		calls = '❌Не заполнено расписание звонков'
	await message.answer(calls, keyboard = keyboard_chat)

@bp.on.chat_message(text='звонки')
async def _(message: Message):
	calls = db.get_calls(message.peer_id)
	if not calls:
		calls = '❌Не заполнено расписание звонков'
	await message.answer(calls, keyboard = keyboard_chat)

@bp.on.chat_message(text = ['/calledit\n<calls>', '/calledit'])
async def _(message: Message, calls: Optional[str] = ''):
	chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
	if message.from_id in db.get_moders(message.peer_id) or message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
		db.edit_calls(message.peer_id, calls)
		await message.answer('Готово!')
		return
	await message.anwer('❌У вас недостаточно прав')