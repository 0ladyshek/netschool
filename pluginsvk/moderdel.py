from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from typing import Optional

bp = Blueprint('moderdel')
db = SQLighter('db.db')
QUERY = [
    "/delmoder",
    "/delmoder <uid:int>",
    "/delmoder [id<uid:int>|@nick]",
    "/delmoder [id<uid:int>|*nick]",
    "/delmoder https://vk.com/id<uid:int>",
]
 
@bp.on.chat_message(text=QUERY)
async def _(message: Message, uid: Optional[int] = None, nick: Optional[str] = None):
    if message.reply_message:
        uid = message.reply_message.from_id
    elif message.fwd_messages:
        uid = message.fwd_messages[0].from_id
    user_id = uid or message.from_id
    chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
    if message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
        db.del_moder(message.peer_id, user_id)
        await message.answer('✅Удалил модератора')