from vkbottle.bot import Blueprint, Message, rules
from sqlighter import SQLighter
import os

db = SQLighter('db.db')
bp = Blueprint('invitechat')

@bp.on.chat_message(rules.ChatActionRule('chat_invite_user'))
async def _(message: Message):
    group = (await bp.api.groups.get_by_id())[0]
    if not db.chat_exists(message.peer_id):
        db.add_chat(message.peer_id)
    if not os.path.exists(f'./chats/{message.peer_id}.txt'):
        with open(f'./chats/{message.peer_id}.txt', 'w') as file:
            pass
    if message.action.member_id == -group.id:
        await message.answer('🙏Спасибо что добавили в беседу, чтобы я видел все сообщения и администраторов выдайте мне администратора!\nДля получения справки напишите команду "/dnevnik"\n\n⚠️Любой, у кого есть аккаунт в боте, может установить аккаунт для незарегистрированных пользователей, подробнее: напишите "/connect" в ЛС бота')