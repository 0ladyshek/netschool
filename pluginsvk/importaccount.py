from vkbottle.bot import Message, Blueprint
from sqlighter import SQLighter
from tools import get_uid
from .keyboard import accounts, keyboard_cancel
from .state import ImportState

db = SQLighter('db.db')
bp = Blueprint('importaccount')

async def importaccount(event):
    await bp.api.messages.send(user_id=event.object.user_id, message='📲Введите токен(токен можно получить командой /me из бота Дискорд или Телеграм)', keyboard = keyboard_cancel, random_id=0)
    await bp.state_dispenser.set(event.object.user_id, ImportState.INTOKEN)

@bp.on.private_message(state=ImportState.INTOKEN)
async def _(message: Message):
    if db.user_exists(token=message.text):
        await message.answer('⏱Начинаю импорт. Ждите!')
        user_accounts = db.get_account_user(token=message.text)
        for account in user_accounts:
            db.add_account_id(get_uid(message.from_id), account)
        keyboard = await accounts(get_uid(message.from_id))
        await message.answer('✅Готово!Теперь вы можете выбрать аккаунты в меню', keyboard=keyboard)
    else:
        keyboard = await accounts(get_uid(message.from_id))
        await message.answer('❌Я не нашел такого токена в базе', keyboard=keyboard)