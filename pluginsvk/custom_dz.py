import datetime
from vkbottle.bot import Blueprint, Message
from sqlighter import SQLighter
from tools import get_uid
from typing import Optional

db = SQLighter('db.db')
bp = Blueprint('custom_dz')

@bp.on.chat_message(text='/dzadd <predmet>:<dz>')
async def _(message: Message, predmet: str, dz: str):
    chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
    if message.from_id in db.get_moders(message.peer_id) or message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
        with open(f'./chats/{message.peer_id}.txt', 'a', encoding='utf-8') as f:
            f.write(predmet + ':' + dz + '\n')
        await message.answer('Готово!')
    else:
        await message.answer('У вас недостаточно прав!')

@bp.on.chat_message(text=['/dzdel <predmet>', '/dzdel'])
async def _(message: Message, predmet: Optional[str] = None):
    chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
    if message.from_id in db.get_moders(message.peer_id) or message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
        if predmet:
            with open(f'./chats/{message.peer_id}.txt', encoding='utf-8') as f:
                lines = f.readlines()
            with open(f'./chats/{message.peer_id}.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    if not line.split(':')[0].lower() == predmet.lower():
                        f.write(line)
        else:
            with open(f'./chats/{message.peer_id}.txt', 'w') as f:
                pass
        await message.answer('Готово!')
    else:
        await message.answer('У вас недостаточно прав!')

@bp.on.chat_message(text='/dzred <predmet>:<dz>')
async def _(message: Message, predmet, dz):
    chat = await bp.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
    if message.from_id in db.get_moders(message.peer_id) or message.from_id in chat.items[0].chat_settings.admin_ids or int(message.from_id) == int(chat.items[0].chat_settings.owner_id):
        with open(f'./chats/{message.peer_id}.txt', encoding='utf-8') as f:
            lines = f.readlines()
        with open(f'./chats/{message.peer_id}.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                if line.split(':')[0].lower() == predmet.lower():
                    line = predmet + ':' + dz + '\n'
                f.write(line)
        await message.answer('Готово!')
    else:
        await message.answer('У вас недостаточно прав!')
