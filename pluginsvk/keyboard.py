from dnevnik import get_student
from vkbottle import Callback, Keyboard, Text
from sqlighter import SQLighter

db = SQLighter('db.db')

keyboard_menu = Keyboard(one_time=True)
keyboard_menu.add(Callback('🗓Расписание', {'dnevnik': 'rasp'}))
keyboard_menu.add(Callback('📓Домашнее задание', {'dnevnik': 'dz'}))
keyboard_menu.row()
keyboard_menu.add(Callback('🗒Просроченные задания', {'dnevnik': 'overdue'}))
keyboard_menu.add(Callback('📌Объявления', {'dnevnik': 'announcements'}))
keyboard_menu.row()
keyboard_menu.add(Callback('1️⃣Оценки', {'dnevnik': 'marks'}))
keyboard_menu.add(Callback('🎉Дни рождения', {'dnevnik': 'birthDays'}))
keyboard_menu.row()
keyboard_menu.add(Callback('🙅‍♂️Удалить аккаунт', {'dnevnik': 'delete'}))
keyboard_menu.add(Callback('📋Выход', {'dnevnik': 'exit'}))
keyboard_menu.add(Callback('🔘Информация', {'dnevnik': 'info'}))
keyboard_menu = keyboard_menu.get_json()

keyboard_date = Keyboard(inline=True)
keyboard_date.add(Callback('📅Вчера', {'date': 'yesterday'}))
keyboard_date.add(Callback('📅Сегодня', {'date': 'today'}))
keyboard_date.add(Callback('📅Завтра', {'date': 'tomorrow'}))
keyboard_date.row()
keyboard_date.add(Callback('📅Неделя', {'date': 'week'}))
keyboard_date.row()
keyboard_date.add(Callback('🚪Назад', {'cmd': 'cancel'}))
keyboard_date = keyboard_date.get_json()

keyboard_delete = Keyboard(inline=True)
keyboard_delete.add(Callback('☑️Да', {'delete': 'yes'}))
keyboard_delete.add(Callback('❌Нет', {'cmd': 'cancel'}))
keyboard_delete = keyboard_delete.get_json()

keyboard_chat = Keyboard(inline=True)
keyboard_chat.add(Text('🗓Расписание', {'chat': 'rasp'}))
keyboard_chat.add(Text('📓Домашнее задание', {'chat': 'dz'}))
keyboard_chat.row()
keyboard_chat.add(Text('1️⃣Оценки', {'chat': 'marks'}))
keyboard_chat.add(Text('🔟Детализация оценок', {'chat': 'detail_mark'}))
keyboard_chat.row()
keyboard_chat.add(Text('🛎Звонки', {'chat': 'calls'}))
keyboard_chat = keyboard_chat.get_json()

keyboard_marks = Keyboard(inline=True)
keyboard_marks.add(Callback('🔟Детализация оценок', {'dnevnik': 'detail_mark'}))
keyboard_marks = keyboard_marks.get_json()

keyboard_birthDays = Keyboard(inline=True)
keyboard_birthDays.add(Callback('👩‍🏫Учителя', {'dnevnik': 'birthStaff'}))
keyboard_birthDays.add(Callback('👪Родители', {'dnevnik': 'birthParent'}))
keyboard_birthDays.add(Callback('👨‍🎓Ученики', {'dnevnik': 'birthStudent'}))
keyboard_birthDays.row()
keyboard_birthDays.add(Callback('🗓За весь год', {'dnevnik': 'birthYear'}))
keyboard_birthDays.row()
keyboard_birthDays.add(Callback('❌Отмена', {'cmd': 'cancel'}))
keyboard_birthDays = keyboard_birthDays.get_json()

keyboard_cancel = Keyboard(inline=True)
keyboard_cancel.add(Callback('❌Отмена', {'cmd': 'cancel'}))
keyboard_cancel = keyboard_cancel.get_json()

keyboard_clean = Keyboard(one_time=True)
keyboard_clean = keyboard_clean.get_json()

async def accounts(uid):
    keyboard = Keyboard(inline=True)
    accounts = db.get_account_user(uid)
    for account in accounts:
        account = db.get_account(account)
        student = await get_student(account[1], account[2], account[3], account[4])
        keyboard.add(Callback(student['nickName'], {'account': str(student['studentId'])}))
        keyboard.row()
    keyboard.add(Callback('✏️Новый аккаунт', {"cmd": "new_account"}))
    return keyboard.get_json()