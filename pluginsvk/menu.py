from vkbottle.bot import Blueprint
from sqlighter import SQLighter
from tools import get_uid
from .keyboard import keyboard_menu

db = SQLighter('db.db')
bp = Blueprint('menu')

async def menu(event):
    await bp.api.messages.send(user_id=event.object.user_id, message='🚪Добро пожаловать в главное меню!', keyboard = keyboard_menu, random_id=0)
    db.edit_account_id(event.object.payload['account'], get_uid(event.object.user_id))