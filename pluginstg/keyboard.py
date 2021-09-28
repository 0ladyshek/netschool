from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from sqlighter import SQLighter
from dnevnik import get_student

db = SQLighter('db.db')

keyboard_menu = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_menu.add(KeyboardButton('🗓Расписание'), KeyboardButton('📓Домашнее задание'))
keyboard_menu.add(KeyboardButton('🗒Просроченные задания'), KeyboardButton('📌Объявления'))
keyboard_menu.add(KeyboardButton('1️⃣Оценки'), KeyboardButton('🎉Дни рождения'))
keyboard_menu.add(KeyboardButton('🙅‍♂️Удалить аккаунт'), KeyboardButton('📋Выход'))
keyboard_menu.add(KeyboardButton('ℹ️Информация'))

keyboard_date = InlineKeyboardMarkup()
keyboard_date.add(InlineKeyboardButton('📅Вчера', callback_data='yesterday'), InlineKeyboardButton('📅Сегодня', callback_data='today'), InlineKeyboardButton('📅Завтра', callback_data='tomorrow'))
keyboard_date.add(InlineKeyboardButton('📅Неделя', callback_data='week'))

keyboard_exit = InlineKeyboardMarkup()
keyboard_exit.add(InlineKeyboardButton('🚪Выход', callback_data='cancel'))

keyboard_delete = InlineKeyboardMarkup()
keyboard_delete.add(InlineKeyboardButton('☑️Да', callback_data='yes_delete'), InlineKeyboardButton('❌Нет', callback_data='cancel'))

keyboard_cancel = InlineKeyboardMarkup()
keyboard_cancel.add(InlineKeyboardButton('⛔️Отмена', callback_data='cancel'))

keyboard_chat = InlineKeyboardMarkup()
keyboard_chat.add(InlineKeyboardButton('🗓Расписание', callback_data='rasp_chat'), InlineKeyboardButton('📓Домашнее задание', callback_data='dz_chat'))
keyboard_chat.add(InlineKeyboardButton('1️⃣Оценки', callback_data='marks_chat'), InlineKeyboardButton('🛎Звонки', callback_data='calls_chat'))

keyboard_marks = InlineKeyboardMarkup()
keyboard_marks.add(InlineKeyboardButton('🔟Детализация оценок', callback_data='detail_marks'))

keyboard_marks_chat = InlineKeyboardMarkup()
keyboard_marks_chat.add(InlineKeyboardButton('🔟Детализация оценок', callback_data='detail_marks_chat'))

keyboard_birth = InlineKeyboardMarkup()
keyboard_birth.add(InlineKeyboardButton('👩‍🏫Учителя', callback_data = 'birthStaff'), InlineKeyboardButton('👪Родители', callback_data = 'birthParrent'), InlineKeyboardButton('👨‍🎓Ученики', callback_data='birthStudent'))
keyboard_birth.add(InlineKeyboardButton('🗓За весь год', callback_data = 'birthYear'))
keyboard_birth.add(InlineKeyboardButton('⛔️Отмена', callback_data='cancel'))

async def keyboard_accounts(uid):
    keyboard = InlineKeyboardMarkup()
    accounts = db.get_account_user(uid)
    for account in accounts:
        account = db.get_account(account)
        student = await get_student(account[1], account[2], account[3], account[4])
        keyboard.add(InlineKeyboardButton(student['nickName'], callback_data = str(student['studentId'])))
    keyboard.add(InlineKeyboardButton('➕Новый аккаунт', callback_data = 'new_profile'))
    return keyboard