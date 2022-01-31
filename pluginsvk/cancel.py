from vkbottle.bot import Blueprint
import json

bp = Blueprint('cancel')

async def cancel(event):
	await bp.state_dispenser.delete(event.object.user_id)
	await bp.api.messages.send_message_event_answer(event_id=event.object.event_id,user_id=event.object.user_id,peer_id=event.object.peer_id,event_data=json.dumps({"type": "show_snackbar", "text": "✅Действие отменено"}))