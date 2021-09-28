from vkbottle.bot import Message, Blueprint
from sqlighter import SQLighter
from tools import get_uid
from dnevnik import get_school, get_student
from .keyboard import accounts, keyboard_cancel
from .state import NewaccountState
import traceback

db = SQLighter('db.db')
bp = Blueprint('registration')

async def registration(event):
    await bp.api.messages.send(user_id=event.object.user_id, message='🖊Введите адрес сетевого города, логин и пароль разделенные пробелом(Пример: https://edu.admoblkaluga.ru/ Аркадий~Петрович ||4R0Ль_йцУk3H").\nЕсли в логине или пароле есть пробелы, то замените их  на ~', keyboard = keyboard_cancel, random_id=0)
    await bp.state_dispenser.set(event.object.user_id, NewaccountState.INLOGIN)

@bp.on.private_message(state=NewaccountState.INLOGIN)
async def _(message: Message):
    logindata = message.text.split(' ')
    if logindata:
        try:
            schools = await get_school(logindata[0])
            await message.answer('📋Введи ID школы из списка ниже(ID - Школа)')
            text = ''
            for school in schools:
                text += f"\n{school['id']} - {school['name']}"
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    await message.answer(text[x:x+4096])
                await message.answer('✅Всё!')
            else:
                await message.answer(text)
            await bp.state_dispenser.set(message.peer_id, NewaccountState.INSCHOOL, logindata=logindata)
        except Exception as e:
            print(traceback.print_exc())
            await message.answer(f'❌Ошибка: {e}\nПопробуйте еще раз или обратитесь к [id350673924|разработчику]')
    else:
        await message.answer('❌Не нашел в твоем сообщении данные, введи еще раз', keyboard = keyboard_cancel)

@bp.on.private_message(state=NewaccountState.INSCHOOL)
async def _(message: Message):
    logindata = message.state_peer.payload["logindata"]
    try:
        student = await get_student(logindata[0], logindata[1], logindata[2], int(message.text))
        db.add_account_id(get_uid(message.from_id), student['studentId'])
        db.add_account(student['studentId'], logindata[0], logindata[1], logindata[2], int(message.text))
        keyboard = await accounts(get_uid(message.from_id))
        await bp.state_dispenser.delete(message.from_id)
        await message.answer('✅Отлично!А теперь перейди в меню и выбери свой аккаунт', keyboard = keyboard)
    except Exception as error:
        await message.answer(f'❌Ошибка: {error}\nПопробуйте еще раз!')