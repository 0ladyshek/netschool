from vkbottle.bot import Blueprint, Message

bp = Blueprint('dz')
bp.labeler.ignore_case = True


@bp.on.chat_message(text="/dz")
async def _(message: Message):
    await message.answer("")