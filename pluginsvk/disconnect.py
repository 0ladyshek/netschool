from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from tools import get_uid

db = SQLighter('db.db')
bp = Blueprint('disconnect')

@bp.on.chat_message(text='/disconnect')
async def _(message: Message):
	chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
	if message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
		db.edit_account_id_chat(message.peer_id)
		await message.answer('✅Отключил аккаунт!')
		return
	accounts = db.get_account_user(get_uid(message.from_id))
	if db.get_account_id_chat(message.peer_id) in accounts:
		db.edit_account_id_chat(message.peer_id)
		await message.answer('✅Отключил аккаунт!')