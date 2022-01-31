import datetime
from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from dnevnik import get_detail_marks
from tools import get_uid
from typing import Optional
from .keyboard import keyboard_chat

db = SQLighter('db.db')
bp = Blueprint('chatdetailmarks')
bp.labeler.ignore_case = True
bp.labeler.vbml_ignore_case = True

@bp.on.chat_message(payload={'chat': 'detail_mark'})
async def _(message: Message):
	if db.user_exists(get_uid(message.from_id)):
		account_id = db.get_account_id(get_uid(message.from_id))
		if not account_id:
			await message.answer("❌Вы не авторизованы в боте")
			return
	else:
		await message.answer("❌Вы не авторизованы в боте")
		return
	account = db.get_account(account_id)
	result = await get_detail_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bp.api.messages.send(user_id=message.from_id, message=result[x:x+4096], random_id=0)
		await bp.api.messages.send(user_id=message.from_id, message='✅Все!', random_id=0)
	else:
		await bp.api.messages.send(user_id=message.from_id, message=result, random_id=0)
	await message.answer('✅Отправил детализацию оценок вам в лс!', keyboard=keyboard_chat)

@bp.on.chat_message(text='доценки')
async def _(message: Message):
	if db.user_exists(get_uid(message.from_id)):
		account_id = db.get_account_id(get_uid(message.from_id))
		if not account_id:
			await message.answer("❌Вы не авторизованы в боте")
			return
	else:
		await message.answer("❌Вы не авторизованы в боте и к чате не подключен аккаунт")
		return
	account = db.get_account(account_id)
	result = await get_detail_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bp.api.messages.send(user_id=message.from_id, message=result[x:x+4096], random_id=0)
		await bp.api.messages.send(user_id=message.from_id, message='✅Все!', random_id=0)
	else:
		await bp.api.messages.send(user_id=message.from_id, message=result, random_id=0)
	await message.answer('✅Отправил детализацию оценок вам в лс!', keyboard=keyboard_chat)
