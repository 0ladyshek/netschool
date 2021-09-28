from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from tools import get_uid

db = SQLighter('db.db')
bp = Blueprint('connect')

@bp.on.chat_message(text='/connect <code>')
async def _(message: Message, code:	int):
	if db.get_account_id_chat(message.peer_id):
		await message.answer('🚫К беседе уже подключен аккаунт.\nЧтобы отключить, тот кто его подключил(или администратор беседы) должен написать /disconnect')
		return
	elif not db.user_exists(get_uid(message.from_id)):
		await message.answer('🛑Вас нет в моей базе!')
		return
	else:
		if db.account_exists(int(code)):
			accounts = db.get_account_user(user_id=get_uid(message.from_id))
			if int(code) in accounts:
				db.edit_account_id_chat(message.peer_id, int(code))
				await message.answer('🔗Подключил ваш аккаунт к беседе\nТеперь все незарегистрированные пользователи будут получать "Расписание" и "Домашнее задание" с вашего аккаунта.\n\nДля получения справки введите "/dnevnik"')
			else:
				await message.answer('❌Вам не принадлежит этот аккаунт!')
		else:
			await message.answer('⛔️Не нашел у себя в базе такого аккаунта')

@bp.on.private_message(text='/connect')
async def _(message: Message):
	account = db.get_account_id(get_uid(message.from_id))
	if account:
		await message.answer(f'🔗Ваша команда для подключения: /connect {account}\n📍Примечание: к беседе не должен быть подключен другой аккаунт(чтобы отвязать аккаунт от беседы, тот кто его привязал или админстратор беседы должен написать /disconnect)')
	else:
		await message.answer('❌Сначала войдите в аккаунт который хотите!')