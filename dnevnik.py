from netschoolapis.netschoolapi import NetSchoolAPI
import re
import datetime
import html2markdown
import numpy as np

async def get_student(url, login, password, school):
	api = NetSchoolAPI(url)
	student = await api.login(login,password,school)
	await api.logout()
	return student

async def get_overdue(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login,password,school)
	overdue = await api.overdue()
	await api.logout()
	return overdue

async def get_marks(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login,password,school)
	period = await api.get_period()
	period = period['filterSources'][2]['defaultValue'].split(' - ')
	start = datetime.datetime.strptime(period[0], '%Y-%m-%dT%H:%M:%S.0000000')
	end = datetime.datetime.strptime(period[1], '%Y-%m-%dT%H:%M:%S.0000000')
	diary = await api.diary(start=start, end=end)
	await api.logout()
	marks = {}
	for days in diary['weekDays']:
		for lesson in days['lessons']:
			if lesson['subjectName'] not in marks.keys():
				marks[lesson['subjectName']] = []
			if 'assignments' in lesson.keys():
				for assignment in lesson['assignments']:
					try:
						if 'mark' in assignment.keys() and 'mark' in assignment['mark']:
							marks[lesson['subjectName']].append(assignment['mark']['mark'])
					except:
						pass
	result = ''
	for lesson in marks.keys():
		if marks[lesson]:
			marks[lesson] = [mark for mark in marks[lesson] if mark]
			if marks[lesson]:
				general_sum = round(sum(marks[lesson]) / len(marks[lesson]), 2)
				marks[lesson] = ' '.join(str(e) for e in marks[lesson])
				result += f"\n{lesson}: {marks[lesson]} | {general_sum}"
	if not result:
		result = '❌Нет оценок'
	return result

async def get_detail_marks(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login,password,school)
	period = await api.get_period()
	period = period['filterSources'][2]['defaultValue'].split(' - ')
	start = datetime.datetime.strptime(period[0], '%Y-%m-%dT%H:%M:%S.0000000')
	end = datetime.datetime.strptime(period[1], '%Y-%m-%dT%H:%M:%S.0000000')
	diary = await api.diary(start=start, end=end)
	await api.logout()
	result = ''
	for days in diary['weekDays']:
		for lesson in days['lessons']:
			if 'assignments' in lesson.keys():
				for assignment in lesson['assignments']:
					if 'mark' in assignment.keys() and 'mark' in assignment['mark']:
						date = datetime.datetime.strptime(assignment['dueDate'], '%Y-%m-%dT%H:%M:%S')
						result += f"\n{date.day}.{date.month} {lesson['subjectName']}: {assignment['mark']['mark']}|{assignment['assignmentName']}"
	if not result:
		result = '❌Нет оценок'
	return result

async def get_announcements(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login,password,school)
	announcements = await api.announcements()
	if announcements:
		result = ''
		files = []
		for announcement in announcements:
			result += f"{announcement['author']['nickName']}({announcement['postDate'].replace('T', ' ')}):\n{announcement['name']}\n{announcement['description']}\n\n"
			for attachment in announcement['attachments']:
				file = await api.download_attachment_as_bytes(attachment)
				files.append({'file': file, 'name': attachment['name']})
		await api.logout()
		result = html2markdown.convert(result)
		clean = re.compile(r'([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
		result = re.sub(clean, '', result)
		return result, files
	else:
		return None, None

async def get_school(url):
	api = NetSchoolAPI(url)
	result = await api.schools()
	await api.close()
	return result

async def get_rasp(url, login, password, school, start, end):
	api = NetSchoolAPI(url)
	await api.login(login,password,school)
	diary = await api.diary(start=start, end=end)
	await api.logout()
	result = '📅Расписание:'
	for day in diary['weekDays']:
		result += f"\n\n🗓День: {re.search('(.*)T00:00:00', day['date']).group(1)}\n"
		for lesson in day['lessons']:
			result += f"{lesson['startTime']} - {lesson['endTime']} {lesson['subjectName']}({lesson['room']})\n"
	return result

async def get_dz(url, login, password, school, start, end):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	diary = await api.diary(start = start, end = end)
	await api.logout()
	result = ''
	result += '📓Домашнее задание:'
	for day in diary['weekDays']:
		result += f"\n\nДень: {re.search('(.*)T00:00:00', day['date']).group(1)}\n"
		for lesson in day['lessons']:
			try:
				for assignment in lesson['assignments']:
					result += f"{lesson['subjectName']}: {assignment['assignmentName']}\n"
			except Exception:
				pass
	return result

async def birthDays(url, login, password, school, student = False, parent = False, staff = False, period = datetime.date.today()):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	birth = await api.birthdayMonth(period)
	await api.logout()
	result = 'Именниники в этом месяце:\n'
	for people in birth:
		if student and people['role'] == 'Ученик':
			result += f'{people["name"]}({people["role"]}) - {people["date"]}\n'
		elif parent and people['role'] == 'Родитель':
			result += f'{people["name"]}({people["role"]}) - {people["date"]}\n'
		elif staff and people['role'] == 'Учитель':
			result += f'{people["name"]}({people["role"]}) - {people["date"]}\n'
	return result

async def birthYears(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	result = 'Именниники в этом году:\n'
	now = datetime.datetime.now()
	start = datetime.date(now.year, 9, 1)
	end = datetime.date(now.year + 1, 8, 31)
	delta = end - start
	for i in range(1, delta.days+1, 31):
		date = start + datetime.timedelta(i)
		result += f"{date.strftime('%B')}:\n"
		birth = await api.birthdayMonth(period=date)
		for people in birth:
			result += f'{people["name"]}({people["role"]}) - {people["date"]}\n'
		result += '\n'
	await api.logout()
	return result

async def getSettings(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	settings = await api.userInfo()
	photo = await api.userPhoto()
	result = '🔐Приватные данные из СГО:\n\n'
	for key in settings.keys():
		result += f'{key}: {settings[key]}\n'
	return result, photo

async def getSchool(url, school):
	api = NetSchoolAPI(url)
	school = await api.school(school)
	result = f"🏫Карточка образовательной организации:"
	result += f"\n🔖Название: {school['commonInfo']['schoolName']}"
	result += f"\n📜Юр. адрес: {school['contactInfo']['postAddress']}"
	if school['commonInfo']['foundingDate']:
		result += f"\n🗓Дата основания: {re.search('(.*)T00:00:00', school['commonInfo']['foundingDate']).group(1)}"
	result += f"\n✉️E-mail: {school['contactInfo']['email']}"
	result += f"\n💻Сайт: {school['contactInfo']['web']}"
	result += f"\n📞Номер телефона: {school['contactInfo']['phones']}"
	result += f"\n🙍‍♂️Директор (Ф.И.О.): {school['managementInfo']['director']}"
	result += f"\n👨‍🏫Заместитель директора по УВР (Ф.И.О.): {school['managementInfo']['principalUVR']}"
	result += f"\n👨‍💻Заместитель директора по ИТ (Ф.И.О.): {school['managementInfo']['principalIT']}"
	result += f"\n👨‍💼Заместитель директора по АХЧ (Ф.И.О.): {school['managementInfo']['principalAHC']}"
	result += f"\n📃ИНН: {school['otherInfo']['inn']}"
	result += f"\n📄Для донатов: {school['bankDetails']['bankScore']}"
	return result

async def getSessions(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	sessions = await api.activeSessions()
	await api.logout()
	result = '👥Активные сессии в СГО:\n'
	i = 0
	for user in sessions:
		i += 1
		result += f"{i}. {user['nickName']}({user['roles']})\n"
	return result

async def getNotify(url, login, password, school, oldmarks):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	period = await api.get_period()
	period = period['filterSources'][2]['defaultValue'].split(' - ')
	start = datetime.datetime.strptime(period[0], '%Y-%m-%dT%H:%M:%S.0000000')
	end = datetime.datetime.strptime(period[1], '%Y-%m-%dT%H:%M:%S.0000000')
	diary = await api.diary(start=start, end=end)
	await api.logout()
	marks = []
	for days in diary['weekDays']:
		for lesson in days['lessons']:
			if 'assignments' in lesson.keys():
				for assignment in lesson['assignments']:
					if 'mark' in assignment.keys() and 'mark' in assignment['mark']:
						if assignment['mark']['mark']:
							date = datetime.datetime.strptime(assignment['dueDate'], '%Y-%m-%dT%H:%M:%S')
							result = html2markdown.convert(f"Новая оценка по {lesson['subjectName']}: {assignment['mark']['mark']} за {assignment['assignmentName']}. Дата: {date.day}.{date.month}")
							clean = re.compile(r'([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
							result = re.sub(clean, '', result)
							marks.append(result)
	difference = [item for item in marks if item not in oldmarks]
	return marks, difference

async def floodLogin(url, login, password, school, count):
	for i in range(count):
		api = NetSchoolAPI(url)
		await api.login(login, password, school)
		await api.close()
	return

async def getHoliday(url, login, password, school, date = datetime.date.today()):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	holidays = await api.holidayMonth(date)
	await api.logout()
	result = '🎊Праздники в этом месяце:'
	for holiday in holidays:
		result += f"\nДень: {holiday['date']}\n"
		for holi in holiday['holidays']:
			result += f"{holi}\n"
	return result

async def getHolidayYear(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	result = '🎊Праздники в этом году'
	calendar = await api.yearView()
	result += f'\n\n📅{calendar[0]}\n📏{calendar[1]}\n🕳{calendar[2]}\n🎉{calendar[3]}\n\n'
	now = datetime.datetime.now()
	start = datetime.date(now.year, 9, 1)
	end = datetime.date(now.year + 1, 8, 31)
	delta = end - start
	for i in range(1, delta.days+1, 31):
		date = start + datetime.timedelta(i)
		result += f"{date.strftime('%B')}:\n"
		holidays = await api.holidayMonth(date)
		for holiday in holidays:
			result += f"День: {holiday['date']}\n"
			for holi in holiday['holidays']:
				result += f"{holi}\n"
		result += '\n'
	await api.logout()
	return result

async def getParentReport(url, login, password, school, term):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	report = await api.parentReport(term)
	await api.logout()
	result = f"🔘Общие:\n5️⃣: {report['total']['5']}\n4️⃣: {report['total']['4']}\n3️⃣: {report['total']['3']}\n2️⃣: {report['total']['2']}\n〰️Средняя: {report['total']['average']}\n🗒Средняя за четверть: {report['total']['average_term']}\n\n"
	for subject in report['subjects'].keys():
		result += f"🔶{subject}:\n5️⃣: {report['subjects'][subject]['5']}\n4️⃣: {report['subjects'][subject]['4']}\n3️⃣: {report['subjects'][subject]['3']}\n2️⃣: {report['subjects'][subject]['2']}\n〰️Средняя: {report['subjects'][subject]['average']}\n🗒За четверть: {report['subjects'][subject]['term']}\n\n"
	return result

async def getTotalReport(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
#	await api.setYear(5811)
	report = await api.reportTotal()
	await api.logout()
	result = '❇️Итоги четвертей:'
	result += '\n1️⃣:\n'
	for subject in report['1']:
		result += f"	{subject}: {report['1'][subject]}\n"
	result += '\n2️⃣:\n'
	for subject in report['2']:
		result += f"	{subject}: {report['2'][subject]}\n"
	result += '\n3️⃣:\n'
	for subject in report['3']:
		result += f"	{subject}: {report['3'][subject]}\n"
	result += '\n4️⃣:\n'
	for subject in report['4']:
		result += f"	{subject}: {report['4'][subject]}\n"
	result += '\n🗓Годовые:\n'
	for subject in report['year']:
		result += f"	{subject}: {report['year'][subject]}\n"
	return result

async def getAverageMark(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	report = await api.reportAverageMark()
	await api.logout()
	result = ''
	for subject in report.keys():
		result += f"{subject}:\n👨‍🎓{report[subject]['student']}\n🎓{report[subject]['class']}\n\n"
	return result

async def getSubjects(url, login, password, school):
	api = NetSchoolAPI(url)
	await api.login(login, password, school)
	diary = await api.diary()
	await api.logout()
	subjects = []
	for days in diary['weekDays']:
		for lesson in days['lessons']:
			if lesson['subjectName'] not in subjects:
				subjects.append(lesson['subjectName'])
	return subjects

async def getMarkSubject(url, login, password, school, subject):
	api = NetSchoolAPI(url)
	await api.login(login,password,school)
	period = await api.get_period()
	period = period['filterSources'][2]['defaultValue'].split(' - ')
	start = datetime.datetime.strptime(period[0], '%Y-%m-%dT%H:%M:%S.0000000')
	end = datetime.datetime.strptime(period[1], '%Y-%m-%dT%H:%M:%S.0000000')
	diary = await api.diary(start=start, end=end)
	await api.logout()
	marks = []
	for days in diary['weekDays']:
		for lesson in days['lessons']:
			if lesson['subjectName'] == subject:
				if 'assignments' in lesson.keys():
					for assignment in lesson['assignments']:
						try:
							if 'mark' in assignment.keys() and 'mark' in assignment['mark']:
								marks.append(assignment['mark']['mark'])
						except:
							pass
	result = ''
	general_sum = 0
	if marks:
		marks = [mark for mark in marks if mark]
		if marks:
			general_sum = round(sum(marks) / len(marks), 2)
			result = ' '.join(str(e) for e in marks)
	return result, general_sum