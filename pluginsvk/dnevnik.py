from vkbottle.bot import Blueprint, Message

bp = Blueprint('dnevnik')
bp.labeler.ignore_case = True

@bp.on.chat_message(text="/dnevnik")
async def _(message: Message):
    await message.answer("")