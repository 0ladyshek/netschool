import datetime
from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from dnevnik import get_dz
from tools import get_uid
from typing import Optional
from .keyboard import keyboard_chat

db = SQLighter('db.db')
bp = Blueprint('dz')
bp.labeler.ignore_case = True
bp.labeler.vbml_ignore_case = True

@bp.on.chat_message(payload={'chat': 'dz'})
async def _(message: Message):
	if db.user_exists(get_uid(message.from_id)):
		account_id = db.get_account_id(get_uid(message.from_id))
		if not account_id:
			account_id = db.get_account_id_chat(message.peer_id)
			if not account_id:
				await message.answer("❌Вы не авторизованы в боте и к чате не подключен аккаунт")
				return
	else:
		account_id = db.get_account_id_chat(message.peer_id)
		if not account_id:
			await message.answer("❌Вы не авторизованы в боте и к чате не подключен аккаунт")
			return
	account = db.get_account(account_id)
	result = await get_dz(account[1], account[2], account[3], account[4], datetime.date.today(), datetime.date.today())
	with open(f'./chats/{message.peer_id}.txt', encoding='utf-8') as f:
		text = f.read()
	if text:
		result += '\n\n🗒Из заметок:\n' + text
	await message.answer(result, keyboard=keyboard_chat)

@bp.on.chat_message(text=['дз', 'дз <data>'])
async def _(message: Message, data: Optional[str] = None):
	if db.user_exists(get_uid(message.from_id)):
		account_id = db.get_account_id(get_uid(message.from_id))
		if not account_id:
			account_id = db.get_account_id_chat(message.peer_id)
			if not account_id:
				await message.answer("❌Вы не авторизованы в боте и к чате не подключен аккаунт")
				return
	else:
		account_id = db.get_account_id_chat(message.peer_id)
		if not account_id:
			await message.answer("❌Вы не авторизованы в боте и к чате не подключен аккаунт")
			return
	if data:
		if data == 'завтра':
			start = datetime.date.today() + datetime.timedelta(days=1)
		elif data == 'вчера':
			start = datetime.date.today() + datetime.timedelta(days=-1)
		elif data == 'неделя':
			start = None
	else:
		start = datetime.date.today()
	account = db.get_account(account_id)
	result = await get_dz(account[1], account[2], account[3], account[4], start, start)
	with open(f'./chats/{message.peer_id}.txt', encoding='utf-8') as f:
		text = f.read()
	if text:
		result += '\n\n🗒Из заметок:\n' + text
	await message.answer(result, keyboard=keyboard_chat)