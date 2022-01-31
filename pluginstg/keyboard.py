from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from sqlighter import SQLighter
from dnevnik import get_student

db = SQLighter('db.db')

keyboard_menu = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_menu.add(KeyboardButton('🗓Расписание'), KeyboardButton('📓Домашнее задание'))
keyboard_menu.add(KeyboardButton('🗒Просроченные задания'), KeyboardButton('📌Объявления'))
keyboard_menu.add(KeyboardButton('1️⃣Оценки'), KeyboardButton('🎉Дни рождения'))
keyboard_menu.add(KeyboardButton('ℹ️Информация'), KeyboardButton('⚙️Настройки'))
keyboard_menu.add(KeyboardButton('⭕️Остальное'), KeyboardButton('🎈Праздники'))
keyboard_menu.add(KeyboardButton('📄Отчёты'))
keyboard_menu.add(KeyboardButton('🙅‍♂️Удалить аккаунт'), KeyboardButton('📋Выход'))

keyboard_date = InlineKeyboardMarkup()
keyboard_date.add(InlineKeyboardButton('📅Вчера', callback_data='yesterday'), InlineKeyboardButton('📅Сегодня', callback_data='today'), InlineKeyboardButton('📅Завтра', callback_data='tomorrow'))
keyboard_date.add(InlineKeyboardButton('📅Неделя', callback_data='week'), InlineKeyboardButton('📅Следующая неделя', callback_data='next_week'))

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

keyboard_info = InlineKeyboardMarkup()
keyboard_info.add(InlineKeyboardButton('🕵️‍♂️Об аккаунте', callback_data='infoStudent'), InlineKeyboardButton('🏫О школе', callback_data='infoSchool'))
keyboard_info.add(InlineKeyboardButton('👀Активные сессии', callback_data='infoSessions'))

keyboard_settings = InlineKeyboardMarkup()
keyboard_settings.add(InlineKeyboardButton('🛎Уведомления о новых оценках', callback_data='notificationNewMarks'))

keyboard_other = InlineKeyboardMarkup()
keyboard_other.add(InlineKeyboardButton('⛔️Флуд логином', callback_data='flood_login'))
keyboard_other.add(InlineKeyboardButton("🔢Калькулятор оценок", callback_data='calc_marks'))

keyboard_holiday = InlineKeyboardMarkup()
keyboard_holiday.add(InlineKeyboardButton('🗓Месяц', callback_data='holiday_month'), InlineKeyboardButton('📅След. месяц', callback_data='holiday_next'))
keyboard_holiday.add(InlineKeyboardButton('🔄За год', callback_data='holiday_year'))

keyboard_report = InlineKeyboardMarkup()
keyboard_report.add(InlineKeyboardButton('✉️Информационное письмо для родителей', callback_data='report_parent'))
keyboard_report.add(InlineKeyboardButton('📇Итоговые оценки', callback_data='report_total'))

keyboard_parent_report = InlineKeyboardMarkup()
keyboard_parent_report.add(InlineKeyboardButton('1️⃣', callback_data='term_1'), InlineKeyboardButton('2️⃣', callback_data='term_2'))
keyboard_parent_report.add(InlineKeyboardButton('3️⃣', callback_data='term_3'), InlineKeyboardButton('4️⃣', callback_data='term_4'))

keyboard_total_report = InlineKeyboardMarkup()
keyboard_total_report.add(InlineKeyboardButton('🔍Средний балл', callback_data='average_mark'))

keyboard_schools = InlineKeyboardMarkup()
keyboard_schools.add(InlineKeyboardButton('🏫Выбрать школу', switch_inline_query_current_chat=''))

keyboard_marks_subject = InlineKeyboardMarkup()
keyboard_marks_subject.add(InlineKeyboardButton('3️⃣', callback_data='3'), InlineKeyboardButton('4️⃣', callback_data='4'))
keyboard_marks_subject.add(InlineKeyboardButton('5️⃣', callback_data='5'))

async def keyboard_accounts(uid):
    keyboard = InlineKeyboardMarkup()
    accounts = db.get_account_user(uid)
    for account in accounts:
        account = db.get_account(account)
        student = await get_student(account[1], account[2], account[3], account[4])
        keyboard.add(InlineKeyboardButton(student['nickName'], callback_data = str(student['studentId'])))
    keyboard.add(InlineKeyboardButton('➕Новый аккаунт', callback_data = 'new_profile'))
    return keyboard

async def keyboard_subjects(subjects):
    keyboard = InlineKeyboardMarkup()
    i = 0
    while i < len(subjects):
        keyboard.add(InlineKeyboardButton(subjects[i], callback_data=f'{i}'))
        i += 1
    keyboard.add(InlineKeyboardButton('⛔️Отмена', callback_data='cancel'))
    return keyboard 