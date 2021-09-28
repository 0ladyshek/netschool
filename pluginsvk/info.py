from vkbottle.bot import Blueprint

bp = Blueprint('info')

async def info(event):
	await bp.api.messages.send(event.object.user_id, 0, message='🔶Создатель: [id350673924|Ёж]\n\n🔸Бот в ТГ: t.me/netschoolbot\n🔹Бот в Дискорде: <в разработке>')