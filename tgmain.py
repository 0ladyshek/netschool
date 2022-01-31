from aiogram import Dispatcher, types, executor
from aiogram.bot import Bot
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import ChatTypeFilter, Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from sqlighter import SQLighter
import logging
import datetime
from dnevnik import *
from pluginstg.keyboard import *
from pluginstg.state import *
import os
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
db = SQLighter('db.db')
bot = Bot(token='')
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)
yes, no = '✅', '❌'

#####Команды#####

@dp.message_handler(commands=['start'], state="*")
async def _(message: types.Message):
	if not db.user_exists(user_id=message.from_user.id):
		db.add_user(message.from_user.id)
	keyboard = await keyboard_accounts(message.from_user.id)
	await message.reply('📜Выбери аккаунт из списка ниже или создай новый', reply_markup = keyboard)
	await Start.menu.set()

@dp.message_handler(ChatTypeFilter('private'), commands=['connect'], state="*")
async def _(message: types.Message):
	account = db.get_account_id(message.from_user.id)
	if account:
		await message.answer(f'🔗Ваша команда для подключения: /connect {account}\n📍Примечание: к беседе не должен быть подключен другой аккаунт(чтобы отвязать аккаунт от беседы, тот кто его привязал или админстратор беседы должен написать /disconnect)')
	else:
		await message.answer('❌Сначала войдите в аккаунт который хотите!')

#####Текстовые кнопки#####

@dp.message_handler(text='🗓Расписание', state="*")
async def _(message: types.Message):
	await message.answer('🗓Выберите дату', reply_markup = keyboard_date)
	await Dnevnik.rasp.set()

@dp.message_handler(text='📓Домашнее задание', state="*")
async def _(message: types.Message):
	await message.answer('🗓Выберите дату', reply_markup = keyboard_date)
	await Dnevnik.home_work.set()

@dp.message_handler(text='🗒Просроченные задания', state="*")
async def _(message: types.Message):
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await get_overdue(account[1], account[2], account[3], account[4])
	resulttext= '🗒Просроченные задания:\n'
	for assignment in result:
		resulttext += f"{assignment['subjectName']}: {assignment['assignmentName']}(Дата сдачи: {re.search('(.*)T00:00:00', assignment['dueDate']).group(1)})\n"
	await message.answer(resulttext)

@dp.message_handler(text='📌Объявления', state="*")
async def _(message: types.Message):
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result, files = await get_announcements(account[1], account[2], account[3], account[4])
	if not result:
		await message.answer('❌Нет объявлений!')
		return
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.answer(result[x:x+4096])
		await message.answer('✅Всё!')
	else:
		await message.answer(result)
	if files:
		await message.answer('📩Вложения из объявлений:')
		for file in files:
			await message.answer_document(document = file['file'], caption = file['name'])

@dp.message_handler(text='1️⃣Оценки', state="*")
async def _(message: types.Message):
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await get_marks(account[1], account[2], account[3], account[4])
	await message.answer(result, reply_markup = keyboard_marks)

@dp.message_handler(text='🎉Дни рождения', state="*")
async def _(message: types.Message):
	await message.answer('📜Выберите кого вам показать', reply_markup = keyboard_birth)

@dp.message_handler(text='🙅‍♂️Удалить аккаунт', state="*")
async def _(message: types.Message):
	await message.answer('⚠️Подтвердите что Вы в здравом уме и светлой памяти согласны на удаление аккаунта', reply_markup=keyboard_delete)

@dp.message_handler(text='📋Выход', state="*")
async def _(message: types.Message):
	db.edit_account_id(0, message.from_user.id)
	await message.answer('✅Все!', reply_markup=ReplyKeyboardRemove())
	keyboard = await keyboard_accounts(message.from_user.id)
	await message.answer('📜Выбери аккаунт из списка ниже или создай новый', reply_markup = keyboard)
	await Start.menu.set()

@dp.message_handler(text='ℹ️Информация', state="*")
async def _(message: types.Message):
	await message.answer('🔶Создатель: @oladushik\n\nБот ВКонтакте: https://vk.com/netschoolbot', reply_markup=keyboard_info)

@dp.message_handler(text='⚙️Настройки', state='*')
async def _(message: types.Message):
	notificationNewMarks = db.get_notification_settings(message.from_user.id)
	await message.answer(f'⚙️Настройки:\n🛎Уведомления: {yes if notificationNewMarks else no}', reply_markup=keyboard_settings)

@dp.message_handler(text='⭕️Остальное', state="*")
async def _(message: types.Message):
	await message.answer('ℹ️Дополнительные команды бота:\n\n☢️Флуд логином(использовать на свой страх и риск): увеличивает кол-во активных сессий на сайте\n➕Калькулятор оценок: подсчитывает сколько оценок нужно до среднего балла', reply_markup=keyboard_other)

@dp.message_handler(text='🎈Праздники', state="*")
async def _(message: types.Message):
	await message.answer('🖊Выберите за какую дату вам предоставить праздники', reply_markup=keyboard_holiday)

@dp.message_handler(text='📄Отчёты', state='*')
async def _(message: types.Message):
	await message.answer('☝️Выберите отчёт', reply_markup=keyboard_report)

##### Инлайн кнопки #####

@dp.callback_query_handler(text='birthStaff', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await birthDays(account[1], account[2], account[3], account[4], staff=True)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='birthStudent', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await birthDays(account[1], account[2], account[3], account[4], student=True)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='birthParrent', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await birthDays(account[1], account[2], account[3], account[4], parent=True)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='birthYear', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await birthYears(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Все!') 
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='detail_marks', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await get_detail_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='yes_delete', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	db.edit_account_id(0, message.from_user.id)
	db.delete_account(account_id, message.from_user.id)
	await message.message.answer('✅Все!', reply_markup=ReplyKeyboardRemove())
	keyboard = await keyboard_accounts(message.from_user.id)
	await message.message.answer('📜Выбери аккаунт из списка ниже или создай новый', reply_markup = keyboard)
	await Start.menu.set()

@dp.callback_query_handler(text='cancel', state='*')
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	await state.finish()
	await message.message.answer('✅Действие отменено')

@dp.callback_query_handler(text='new_profile', state='Start:menu')
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	await message.message.answer('🖊Введите адрес сетевого города, логин и пароль разделенные пробелом(Пример: https://edu.admoblkaluga.ru/ Аркадий~Петрович P4R0Ль_йцУk3H").\nЕсли в логине или пароле есть пробелы, то замените их  на ~', reply_markup=keyboard_cancel)
	await Start.next()

@dp.callback_query_handler(state='Start:menu')
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	try:
		account_id = int(message.data)
	except:
		keyboard = await keyboard_accounts(message.from_user.id)
		await message.message.answer('❌Пожалуйста, нажмите на кнопку с аккаунтом', reply_markup = keyboard)
		return
	if account_id in db.get_account_user(message.from_user.id):
		db.edit_account_id(account_id, message.from_user.id)
		await message.message.answer('🚪Добро пожаловать', reply_markup=keyboard_menu)
		await state.finish()
		return
	keyboard = await keyboard_accounts(message.from_user.id)
	await message.message.answer('❌Пожалуйста, нажмите на кнопку с аккаунтом', reply_markup = keyboard)

@dp.callback_query_handler(text='infoStudent', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result, photo = await getSettings(account[1], account[2], account[3], account[4])
	await message.message.answer_photo(caption=result, photo = photo.content)

@dp.callback_query_handler(text='infoSchool', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await getSchool(account[1], account[4])
	await message.message.answer(result)

@dp.callback_query_handler(text='infoSessions', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await getSessions(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='notificationNewMarks', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	notification = db.get_notification_settings(message.from_user.id)
	notification = 1 if not notification else 0
	db.edit_notify(message.from_user.id, notification)
	await message.message.answer(f'✅Установил значение: {yes if bool(notification) else no}')

@dp.callback_query_handler(text='flood_login', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	await message.message.answer('✏️Введите кол-во логинов', reply_markup=keyboard_cancel)
	await Other.action.set()

@dp.callback_query_handler(text='calc_marks', state='*')
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	subjects = await getSubjects(account[1], account[2], account[3], account[4])
	keyboard = await keyboard_subjects(subjects)
	await message.message.answer("🔍Выберите предмет, по которому надо посчитать оценки", reply_markup=keyboard)
	await Other.get_subject.set()

@dp.callback_query_handler(state='Other:get_subject')
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	subject = (await getSubjects(account[1], account[2], account[3], account[4]))[int(message.data)]
	marks, average = await getMarkSubject(account[1], account[2], account[3], account[4], subject)
	if not marks:
		await message.message.answer('❌Нет оценок по этому предмету')
		return await state.finish()
	await message.message.answer(f'0️⃣Оценки по этому предмету: {marks}\n⤴️Средний балл: {average}\n\n❓Какую оценку вы хотите?', reply_markup=keyboard_marks_subject)
	await state.update_data(marks=marks, average=average)
	await Other.next()

@dp.callback_query_handler(state='Other:get_mark')
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	data = await state.get_data()
	marks = data['marks'].split(' ')
	if int(message.data) <= int(data['average']):
		await message.message.answer('❌Вы уже достигли нужного результата')
		return await state.finish()
	general_sum = 0
	count_marks = len(marks)
	for mark in marks:
		general_sum += int(mark)
	if int(message.data) == 3:
		count_three_to_two_eight = 0
		general_sum_three_to_three = general_sum
		count_marks_three_to_three = count_marks
		average_three_to_three = round(general_sum / count_marks, 1)
		while average_three_to_three < 2.8:
			count_three_to_two_eight += 1
			count_marks_three_to_three += 1
			general_sum_three_to_three += 3
			average_three_to_three = round(general_sum_three_to_three / count_marks_three_to_three, 1)
			if count_three_to_two_eight > 50:
				average_three_to_three = 2.8
		count_three_to_two_nine = count_three_to_two_eight
		while average_three_to_three < 2.9:
			count_three_to_two_nine += 1
			count_marks_three_to_three += 1
			general_sum_three_to_three += 3
			average_three_to_three = round(general_sum_three_to_three / count_marks_three_to_three, 1)
			if count_three_to_two_nine > 50:
				average_three_to_three = 2.9
		count_three_to_three = count_three_to_two_eight
		while average_three_to_three < 3:
			count_three_to_three += 1
			count_marks_three_to_three += 1
			general_sum_three_to_three += 3
			average_three_to_three = round(general_sum_three_to_three / count_marks_three_to_three, 1)
			if count_three_to_three > 50:
				average_three_to_three = 3
		await message.message.answer(f'📈Количество троек:\nДо 2️⃣.8️⃣:{count_three_to_two_eight}\nДо 2️⃣.9️⃣: {count_three_to_two_nine}\nДо 3️⃣: {count_three_to_three}')
		count_for_to_two_eight = 0
		general_sum_for_to_three = general_sum
		count_marks_for_to_three = count_marks
		average_for_to_three = round(general_sum / count_marks, 1)
		while average_for_to_three < 2.8:
			count_for_to_two_eight += 1
			count_marks_for_to_three += 1
			general_sum_for_to_three += 4
			average_for_to_three = round(general_sum_for_to_three / count_marks_for_to_three, 1)
			if count_for_to_two_eight > 50:
				average_for_to_three = 2.8
		count_for_to_two_nine = count_for_to_two_eight
		while average_for_to_three < 2.9:
			count_for_to_two_nine += 1
			count_marks_for_to_three += 1
			general_sum_for_to_three += 4
			average_for_to_three = round(general_sum_for_to_three / count_marks_for_to_three, 1)
			if count_for_two_nine > 50:
				average_three_to_three = 2.9
		count_for_to_three = count_for_to_two_eight
		while average_for_to_three < 3:
			count_for_to_three += 1
			count_marks_for_to_three += 1
			general_sum_for_to_three += 4
			average_for_to_three = round(general_sum_for_to_three / count_marks_for_to_three, 1)
			if count_for_to_three > 50:
				average_three_to_three = 3
		await message.message.answer(f'📈Количество четверок:\nДо 2️⃣.8️⃣:{count_for_to_two_eight}\nДо 2️⃣.9️⃣: {count_for_to_two_nine}\nДо 3️⃣: {count_for_to_three}')
		count_five_to_two_eight = 0
		general_sum_five_to_three = general_sum
		count_marks_five_to_three = count_marks
		average_five_to_three = round(general_sum / count_marks, 1)
		while average_five_to_three < 2.8:
			count_five_to_two_eight += 1
			count_marks_five_to_three += 1
			general_sum_five_to_three += 4
			average_five_to_three = round(general_sum_five_to_three / count_marks_five_to_three, 1)
			if count_five_to_two_eight > 50:
				average_five_to_three = 2.8
		count_five_to_two_nine = count_five_to_two_eight
		while average_five_to_three < 2.9:
			average_five_to_three += 1
			count_marks_five_to_three += 1
			general_sum_five_to_three += 4
			average_five_to_three = round(general_sum_five_to_three / count_marks_five_to_three, 1)
			if average_five_to_three > 50:
				average_five_to_three = 2.9
		count_five_to_three = count_five_to_two_eight
		while average_five_to_three < 3:
			count_five_to_three += 1
			count_marks_five_to_three += 1
			general_sum_five_to_three += 4
			average_five_to_three = round(general_sum_five_to_three / count_marks_five_to_three, 1)
			if count_five_to_three > 50:
				average_three_to_three = 3
		await message.message.answer(f'📈Количество пятерок:\nДо 2️⃣.8️⃣:{count_five_to_two_eight}\nДо 2️⃣.9️⃣: {count_five_to_two_nine}\nДо 3️⃣: {count_five_to_three}')
		return await state.finish()
	if int(message.data) == 4:
		count_for_to_three_eight = 0
		general_sum_for_to_for = general_sum
		count_marks_for_to_for = count_marks
		average_for_to_for = round(general_sum / count_marks, 1)
		while average_for_to_for < 3.8:
			count_for_to_three_eight += 1
			count_marks_for_to_for += 1
			general_sum_for_to_for += 4
			average_for_to_for = round(general_sum_for_to_for / count_marks_for_to_for, 1)
			if count_for_to_three_eight > 50:
				average_for_to_for = 3.8
		count_for_to_three_nine = count_for_to_three_eight
		while average_for_to_for < 3.9:
			count_for_to_three_nine += 1
			count_marks_for_to_for += 1
			general_sum_for_to_for += 4
			average_for_to_for = round(general_sum_for_to_for / count_marks_for_to_for, 1)
			if count_for_to_three_nine > 50:
				average_for_to_for = 3.9
		count_for_to_for = count_for_to_three_nine
		while average_for_to_for < 4:
			count_for_to_for += 1
			count_marks_for_to_for += 1
			general_sum_for_to_for += 4
			average_for_to_for = round(general_sum_for_to_for / count_marks_for_to_for, 1)
			if count_for_to_for > 50:
				average_for_to_for = 3
		await message.message.answer(f'📈Количество четверок:\nДо 3️⃣.8️⃣:{count_for_to_three_eight}\nДо 3️⃣.9️⃣: {count_for_to_three_nine}\nДо 4️⃣: {count_for_to_for}')
		count_five_to_three_eight = 0
		general_sum_five_to_for = general_sum
		count_marks_five_to_for = count_marks
		average_five_to_for = round(general_sum / count_marks, 1)
		while average_five_to_for < 3.8:
			count_five_to_three_eight += 1
			count_marks_five_to_for += 1
			general_sum_five_to_for += 5
			average_five_to_for = round(general_sum_five_to_for / count_marks_five_to_for, 1)
			if count_five_to_three_eight > 50:
				average_five_to_for = 3.8
		count_five_to_three_nine = count_five_to_three_eight
		while average_five_to_for < 3.9:
			count_for_to_two_nine += 1
			count_marks_five_to_for += 1
			general_sum_five_to_for += 5
			average_five_to_for = round(general_sum_five_to_for / count_marks_five_to_for, 1)
			if count_five_to_three_nine > 50:
				average_five_to_for = 3.9
		count_five_to_for = count_five_to_three_nine
		while average_five_to_for < 4:
			count_five_to_for += 1
			count_marks_five_to_for += 1
			general_sum_five_to_for += 4
			average_five_to_for = round(general_sum_five_to_for / count_marks_five_to_for, 1)
			if count_five_to_for > 50:
				average_five_to_for = 4
		await message.message.answer(f'📈Количество пятерок:\nДо 2️⃣.8️⃣:{count_five_to_three_eight}\nДо 2️⃣.9️⃣: {count_five_to_three_nine}\nДо 3️⃣: {count_five_to_for}')
		return await state.finish()
	if int(message.data) == 5:
		count_five_to_for_eight = 0
		general_sum_five_to_five = general_sum
		count_marks_five_to_five = count_marks
		average_five_to_five = round(general_sum / count_marks, 1)
		while average_five_to_five < 4.8:
			count_five_to_for_eight += 1
			count_marks_five_to_five += 1
			general_sum_five_to_five += 5
			average_five_to_five = round(general_sum_five_to_five / count_marks_five_to_five, 1)
			if count_five_to_for_eight > 50:
				average_five_to_five = 4.8
		count_five_to_for_nine = count_five_to_for_eight
		while average_five_to_five < 4.9:
			count_five_to_for_nine += 1
			count_marks_five_to_five += 1
			general_sum_five_to_five += 5
			average_five_to_five = round(general_sum_five_to_five / count_marks_five_to_five, 1)
			if count_five_to_for_nine > 50:
				average_five_to_five = 4.9
		count_five_to_five = count_five_to_for_nine
		while average_five_to_five < 5:
			count_five_to_five += 1
			count_marks_five_to_five += 1
			general_sum_five_to_five += 5
			average_five_to_five = round(general_sum_five_to_five / count_marks_five_to_five, 1)
			if count_five_to_five > 50:
				average_five_to_five = 5
		await message.message.answer(f'📈Количество пятерок:\nДо 4️⃣.8️⃣:{count_five_to_for_eight}\nДо 4️⃣.9️⃣: {count_five_to_for_nine}\nДо 5️⃣: {count_five_to_five}')
		return await state.finish()

@dp.callback_query_handler(text='holiday_month', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await getHoliday(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='holiday_next', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	date = datetime.date.today() + datetime.timedelta(days=31)
	result = await getHoliday(account[1], account[2], account[3], account[4], date)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='holiday_year', state="*")
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await getHolidayYear(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='report_parent', state='*')
async def _(message: types.CallbackQuery):
	await message.answer()
	await message.message.answer('🗓Выбери четверть', reply_markup=keyboard_parent_report)

@dp.callback_query_handler(text=['term_1', 'term_2', 'term_3', 'term_4'], state='*')
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	term = int(message.data.split('_')[1])
	result = await getParentReport(account[1], account[2], account[3], account[4], term)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='report_total', state='*')
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await getTotalReport(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!', reply_markup=keyboard_total_report)
	else:
		await message.message.answer(result, reply_markup=keyboard_total_report)

@dp.callback_query_handler(text='average_mark', state='*')
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	result = await getAverageMark(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

##### Работа после старта #####

@dp.inline_handler(state='Start:schools')
async def _(message: types.InlineQuery, state: FSMContext):
	query_offset = int(message.offset) if message.offset else 0
	logindata = (await state.get_data())['logindata'].split(' ')
	url = logindata[0]
	schools = await get_school(url)
	if message.query:
		school_query = []
		for school in schools:
			if message.query in school['name']:
				print(school['name'])
				school_query.append(school)
		schools = school_query
	result = [types.InlineQueryResultArticle(
        id=item['id'],
        title=item['name'],
        input_message_content=types.InputTextMessageContent(
            message_text=f"{item['id']}",
        ),
    ) for item in schools[query_offset:]]
	if len(result) < 50:
		await message.answer(result, is_personal=True, next_offset="")
	else:
		await message.answer(result[:50], is_personal=True, next_offset=str(query_offset+50))

@dp.message_handler(state='Start:new_account')
async def _(message: types.Message, state: FSMContext):
	await state.update_data(logindata=message.text, page=1)
	await message.answer('📋Теперь пришло время выбрать школу\nВведи ID школы из списка ниже(ID - Школа) или воспользуйся кнопкой')
	url = message.text.split(' ')[0]
	schools = await get_school(url)
	text = ''
	for school in schools:
		text += f"\n{school['id']} - {school['name']}"
	if len(text) > 4096:
		for x in range(0, len(text), 4096):
			await message.answer(text[x:x+4096])
		await message.answer('✅Всё!', reply_markup=keyboard_schools)
	else:
		await message.answer(text, reply_markup=keyboard_schools)
	await Start.next()

@dp.message_handler(state='Start:schools')
async def _(message: types.Message, state: FSMContext):
	logindata = (await state.get_data())['logindata'].split(' ')
	try:
		student = await get_student(logindata[0], logindata[1], logindata[2], int(message.text))
		db.add_account_id(message.from_user.id, student['studentId'])
		db.add_account(student['studentId'], logindata[0], logindata[1], logindata[2], int(message.text))
		keyboard = await keyboard_accounts(message.from_user.id)
		await message.answer('✅Отлично!Теперь выберите аккаунт из меню', reply_markup=keyboard)
	except Exception as e:
		keyboard = await keyboard_accounts(message.from_user.id)
		await message.answer(f'❌Ошибка: {e}\nПройдите регистрацию заново или обратитесь к @oladushik', reply_markup=keyboard)
	await Start.menu.set()

##### Расписание и ДЗ #####

@dp.callback_query_handler(text='yesterday', state=["Dnevnik:rasp", "Dnevnik:home_work"])
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	state = await state.get_state()
	start = end = datetime.date.today() + datetime.timedelta(days=-1)
	if state == 'Dnevnik:rasp':
		result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	elif state == 'Dnevnik:home_work':
		result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='today', state=["Dnevnik:rasp", "Dnevnik:home_work"])
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	state = await state.get_state()
	start = end = datetime.date.today()
	if state == 'Dnevnik:rasp':
		result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	elif state == 'Dnevnik:home_work':
		result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='tomorrow', state=["Dnevnik:rasp", "Dnevnik:home_work"])
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	state = await state.get_state()
	start = end = datetime.date.today() + datetime.timedelta(days=1)
	if state == 'Dnevnik:rasp':
		result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	elif state == 'Dnevnik:home_work':
		result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='week', state=["Dnevnik:rasp", "Dnevnik:home_work"])
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	state = await state.get_state()
	start = end = None
	if state == 'Dnevnik:rasp':
		result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	elif state == 'Dnevnik:home_work':
		result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

@dp.callback_query_handler(text='next_week', state=["Dnevnik:rasp", "Dnevnik:home_work"])
async def _(message: types.CallbackQuery, state: FSMContext):
	await message.answer()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	state = await state.get_state()
	start = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday() - 7)
	end = start + datetime.timedelta(days=5)
	if state == 'Dnevnik:rasp':
		result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	elif state == 'Dnevnik:home_work':
		result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await message.message.answer(result[x:x+4096])
		await message.message.answer('✅Всё!')
	else:
		await message.message.answer(result)

##### Работа в беседах #####

@dp.my_chat_member_handler()
async def _(my_chat_member: types.ChatMemberUpdated):
	if not db.chat_exists(my_chat_member.chat.id):
		db.add_chat(my_chat_member.chat.id)
	if not os.path.isfile(f'./chats/{my_chat_member.chat.id}.txt'):
		with open(f'./chats/{my_chat_member.chat.id}.txt', 'w') as f:
			pass
	group_id = await bot.get_me()
	if my_chat_member.new_chat_member.user.id == group_id.id:
		if my_chat_member.new_chat_member.status == 'member' and my_chat_member.old_chat_member.status == 'left':
			await bot.send_message(my_chat_member.chat.id, '🙏Спасибо что добавили в беседу\nДля получения справки напишите команду "/dnevnik"\n\n⚠️Любой, у кого есть аккаунт в боте, может установить аккаунт для незарегистрированных пользователей, подробнее: напишите "/connect" в ЛС бота')

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), commands=['dnevnik'])
async def _(message: types.Message):
	await message.answer('https://telegra.ph/Spravka-po-ispolzovaniyu-bota-v-besede-09-23')

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), commands=['dz'])
async def _(message: types.Message):
	await message.answer('https://telegra.ph/Spravka-po-dobavleniyu-kastomnogo-DZ-08-22')

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), commands=['connect'])
async def _(message: types.Message):
	account_id = int(message.text.split(' ')[1])
	if not db.account_exists(account_id):
		await message.answer('❌Не нашел этого аккаунта у себя в базе')
		return
	if db.user_exists(message.from_user.id):
		if not account_id in db.get_account_user(message.from_user.id):
			await message.answer('❌Вам не принадлежит этот аккаунт')
			return
	if db.get_account_id_chat(message.chat.id):
		await message.answer('❌К беседе уже подключен аккаунт')
		return
	db.edit_account_id_chat(message.chat.id, account_id)
	await message.answer('✅Подключил аккаунт к беседе!Теперь все незарегистрированные пользователи будут получать информацию с вашего аккаунта(кроме оценок)!', reply_markup = keyboard_chat)

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), commands=['disconnect'])
async def _(message: types.Message):
	admins = await bot.get_chat_administrators(message.chat.id)
	for admin in admins:
		if admin['user']['id'] == message.from_user.id:
			db.edit_account_id_chat(message.chat.id)
			await message.answer('✅Отключил аккаунт от беседы')
			return
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id_chat(message.chat.id)
		if account_id in db.get_account_user(message.from_user.id):
			db.edit_account_id_chat(message.chat.id)
			await message.answer('✅Отключил аккаунт от беседы')
			return
	await message.answer('❌Вы не админ и вам не принадлежит этот аккаунт')

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), Text(ignore_case=True, equals=['расписание', 'расписание завтра', 'расписание вчера', 'расписание неделя']))
async def _(message: types.Message):
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	else:
		account_id = db.get_account_id_chat(message.chat.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте и к чату не подключен аккаунт!', reply_markup = keyboard_chat)
		return
	account = db.get_account(account_id)
	start = end = datetime.date.today()
	if len(message.text.split(' ')) > 1:
		date = message.text.split(' ')[1]
		if date == 'завтра':
			start = end = datetime.date.today() + datetime.timedelta(days=1)
		elif date == 'вчера':
			start = end = datetime.date.today() + datetime.timedelta(days=-1)
		elif date == 'неделя':
			start = end = None
	result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	await message.answer(result, reply_markup=keyboard_chat)

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), Text(ignore_case=True, equals=['дз', 'дз завтра', 'дз вчера', 'дз неделя']))
async def _(message: types.Message):
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	else:
		account_id = db.get_account_id_chat(message.chat.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте и к чату не подключен аккаунт!', reply_markup = keyboard_chat)
		return
	account = db.get_account(account_id)
	start = end = datetime.date.today()
	if len(message.text.split(' ')) > 1:
		date = message.text.split(' ')[1]
		if date == 'завтра':
			start = end = datetime.date.today() + datetime.timedelta(days=1)
		elif date == 'вчера':
			start = end = datetime.date.today() + datetime.timedelta(days=-1)
		elif date == 'неделя':
			start = end = None
	result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	with open(f'./chats/{message.chat.id}.txt', encoding='utf-8') as f:
		text = f.read()
	if text:
		result += '\n\n🗒Из заметок:\n' + text
	await message.answer(result, reply_markup=keyboard_chat)

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), Text(ignore_case=True, equals=['оценки']))
async def _(message: types.Message):
	account_id = 0
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте!')
		return
	account = db.get_account(account_id)
	result = await get_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bot.send_message(message.from_user.id, result[x:x+4096])
		await bot.send_message(message.from_user.id, '✅Всё!')
	else:
		await bot.send_message(message.from_user.id, result)
	await message.answer('✅Отправил оценки вам в ЛС!', reply_markup=keyboard_chat)

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), Text(ignore_case=True, equals=['доценки']))
async def _(message: types.Message):
	account_id = 0
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте!')
		return
	account = db.get_account(account_id)
	result = await get_detail_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bot.send_message(message.from_user.id, result[x:x+4096])
		await bot.send_message(message.from_user.id, '✅Всё!')
	else:
		await bot.send_message(message.from_user.id, result)
	await message.answer('✅Отправил оценки вам в ЛС!', reply_markup=keyboard_chat)

@dp.message_handler(ChatTypeFilter(['group', 'supergroup']), Text(ignore_case=True, equals=['звонки']))
async def _(message: types.Message):
	calls = db.get_calls(message.chat.id)
	if not calls:
		calls = '❌В беседе не заполнено расписание звонков'
	await message.answer(calls, reply_markup = keyboard_chat)

@dp.callback_query_handler(text='rasp_chat')
async def _(message: types.CallbackQuery):
	await message.answer()
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	else:
		account_id = db.get_account_id_chat(message.message.chat.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте и к чату не подключен аккаунт!', reply_markup = keyboard_chat)
		return
	account = db.get_account(account_id)
	start = end = datetime.date.today()
	result = await get_rasp(account[1], account[2], account[3], account[4], start, end)
	await message.message.answer(result, reply_markup=keyboard_chat)

@dp.callback_query_handler(text='dz_chat')
async def _(message: types.CallbackQuery):
	await message.answer()
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	else:
		account_id = db.get_account_id_chat(message.message.chat.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте и к чату не подключен аккаунт!', reply_markup = keyboard_chat)
		return
	account = db.get_account(account_id)
	start = end = datetime.date.today()
	result = await get_dz(account[1], account[2], account[3], account[4], start, end)
	with open(f'./chats/{message.message.chat.id}.txt', encoding='utf-8') as f:
		text = f.read()
	if text:
		result += '\n\n🗒Из заметок:\n' + text
	await message.message.answer(result, reply_markup=keyboard_chat)

@dp.callback_query_handler(text='marks_chat')
async def _(message: types.CallbackQuery):
	await message.answer()
	account_id = 0
	if db.user_exists(message.from_user.id):
		account_id = db.get_account_id(message.from_user.id)
	if not account_id:
		await message.answer('❌Вы не авторизованы в боте!')
		return
	account = db.get_account(account_id)
	result = await get_marks(account[1], account[2], account[3], account[4])
	if len(result) > 4096:
		for x in range(0, len(result), 4096):
			await bot.send_message(message.from_user.id, result[x:x+4096])
		await bot.send_message(message.from_user.id, '✅Всё!')
	else:
		await bot.send_message(message.from_user.id, result)
	await message.message.answer('✅Отправил оценки вам в ЛС!', reply_markup=keyboard_marks)

@dp.callback_query_handler(text='calls_chat')
async def _(message: types.CallbackQuery):
	await message.answer()
	calls = db.get_calls(message.message.chat.id)
	if not calls:
		calls = '❌В беседе не заполнено расписание звонков'
	await message.message.answer(calls, reply_markup = keyboard_chat)

##### Работа с кастомным дз и звонками #####

@dp.message_handler(Text(startswith='/calledit'), is_chat_admin=True)
async def _(message: types.Message):
	calls = ''
	if message.text[9:]:
		calls = message.text[9:]
	db.edit_calls(message.chat.id, calls)
	await message.answer('✅Установил расписание звонков', reply_markup=keyboard_chat)
	return
	
@dp.message_handler(Text(startswith='/addmoder'), is_chat_admin=True)
async def _(message: types.Message):
	if not message.text[10:]:
		await message.answer('❌Укажите ID')
		return
	db.add_moder(message.chat.id, int(message.text[10:]))
	await message.answer('✅Добавил модератора')

@dp.message_handler(Text(startswith='/delmoder'), is_chat_admin=True)
async def _(message: types.Message):
	if not message.text[10:]:
		await message.answer('❌Укажите ID')
		return
	db.del_moder(message.chat.id, int(message.text[10:]))
	await message.answer('✅Удалил модератора')

@dp.message_handler(text='/moders', is_chat_admin=True)
async def _(message: types.Message):
	result = 'Доверенные лица беседы:'
	for moder in db.get_moders(message.chat.id):
		try:
			user = (await bot.get_chat_member(message.chat.id, moder)).user
			result += f'\n@{user.username}'
		except Exception:
			pass
	await message.answer(result)

@dp.message_handler(Text(startswith='/dzadd'))
async def _(message: types.Message):
	dz = message.text[7:]
	if not dz:
		await message.answer('❌Вы не написали что надо добавить')
		return
	admin = False
	admins = await bot.get_chat_administrators(message.chat.id)
	for admin in admins:
		if admin['user']['id'] == message.from_user.id:
			admin = True
	if message.from_user.id in db.get_moders(message.chat.id):
		admin = True
	if admin:
		with open(f'./chats/{message.chat.id}.txt', 'a') as f:
			f.write(f'{dz}\n')
		await message.answer('✅Готово')
	else:
		await message.answer('❌У вас недостаточно прав')

@dp.message_handler(Text(startswith='/dzdel'))
async def _(message: types.Message):
	admin = False
	admins = await bot.get_chat_administrators(message.chat.id)
	for admin in admins:
		if admin['user']['id'] == message.from_user.id:
			admin = True
	if message.from_user.id in db.get_moders(message.chat.id):
		admin = True
	if admin:
		dz = message.text.split(' ')
		if not len(dz) > 1:
			with open(f'./chats/{message.chat.id}.txt', 'w') as f:
				pass
		else:
			with open(f'./chats/{message.chat.id}.txt') as f:
				lines = f.readlines()
			with open(f'./chats/{message.chat.id}.txt', 'w') as f:
				for line in lines:
					if not line.split(':')[0].lower() == dz[1].split(':')[0].lower():
						f.write(line)
		await message.answer('✅Готово')

@dp.message_handler(Text(startswith='/dzred'))
async def _(message: types.Message):
	admin = False
	admins = await bot.get_chat_administrators(message.chat.id)
	for admin in admins:
		if admin['user']['id'] == message.from_user.id:
			admin = True
	if message.from_user.id in db.get_moders(message.chat.id):
		admin = True
	if admin:
		dz = message.text[7:]
		if not dz:
			await message.answer('❌Вы не указали ДЗ')
			return
		predmet = dz.split(':')[0]
		dz = dz.split(':')[1]
		with open(f'./chats/{message.chat.id}.txt') as f:
			lines = f.readlines()
		with open(f'./chats/{message.chat.id}.txt', 'w') as f:
			for line in lines:
				if line.split(':')[0].lower() == predmet.lower():
					line = predmet + ':' + dz + '\n'
				f.write(line)
		await message.answer('✅Готово')

##### Остальное #####

@dp.message_handler(state='Other:action')
async def _(message: types.Message, state: FSMContext):
	await message.answer('✅Запускаю')
	await state.finish()
	account_id = db.get_account_id(message.from_user.id)
	account = db.get_account(account_id)
	await floodLogin(account[1], account[2], account[3], account[4], int(message.text))
	await message.answer('☑️Закончил флуд')

async def send_notiifcation(dp: Dispatcher):
	users = db.get_notification_users()
	for user in users:
		try:
			if user[1]:
				account = db.get_account(user[1])	
				marks, result = await getNotify(account[1], account[2], account[3], account[4], account[5])
				db.edit_marks(user[1], marks)
				for mark in result:
					await dp.bot.send_message(user[0], mark)
				logging.info(f'Send {user[0]} notify')			
		except Exception as e:
			logging.warning(f'Error send {user[0]} notify: {e}')

def notiication():
	scheduler.add_job(send_notiifcation, "interval", minutes=5, args=(dp,))

async def on_startup(dp):
	notiication()

scheduler.start()
executor.start_polling(dp, on_startup=on_startup)