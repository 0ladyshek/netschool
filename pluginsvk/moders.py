from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter

db = SQLighter('db.db')
bp = Blueprint('moders')

@bp.on.chat_message(text="/moders")
async def _(message: Message):
    chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
    if message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
        moders = db.get_moders(message.peer_id)
        result = '⭐️Список доверенных лиц:'
        for moder in moders:
            user = (await bp.api.users.get(user_id=moder))[0]
            result += f'\n[id{moder}|{user.first_name} {user.last_name}]'
        await message.answer(result)
    else:
        await message.answer('❌У вас недостаточно прав')