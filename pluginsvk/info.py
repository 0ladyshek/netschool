from vkbottle.bot import Blueprint
from .keyboard import keyboard_info
from sqlighter import SQLighter
from dnevnik import getSchool, getSessions, getSettings
from vkbottle.tools import PhotoMessageUploader

bp = Blueprint('info')

async def info(event):
	await bp.api.messages.send(event.object.user_id, 0, message='🔶Создатель: [id350673924|Ёж]\n\n🔸Бот в ТГ: t.me/netschoolbot\n🔹Бот в Дискорде: <в разработке>', keyboard=keyboard_info)

async def infoStudent(event):
	account = db.get_account(db.get_account_id(get_uid(event.object.user_id)))
	result, photo = await getSettings(account[1], account[2], account[3], account[4])
	photo = await PhotoMessageUploader(bp.api).upload(
        photo.content, peer_id=event.object.peer_id
    )
	await bp.api.messages.send(event.object.user_id, 0, message=result, attachment=photo)