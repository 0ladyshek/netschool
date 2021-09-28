from netschoolapis.netschoolapi import NetSchoolAPI
import re
import datetime
import html2markdown

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
					if 'mark' in assignment.keys() and 'mark' in assignment['mark']:
						marks[lesson['subjectName']].append(assignment['mark']['mark'])
	result = ''
	for lesson in marks.keys():
		if marks[lesson]:
			marks[lesson] = [mark for mark in marks[lesson] if mark]
			general_sum = round(sum(marks[lesson]) / len(marks[lesson]), 1)
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
	await api.logout()
	if announcements:
		result = ''
		for announcement in announcements:
			result += f"{announcement['author']['nickName']}({announcement['postDate'].replace('T', ' ')}): {announcement['description']}\n"
		result = html2markdown.convert(result)
		clean = re.compile(r'([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
		result = re.sub(clean, '', result)
		return result
	else:
		return '❌Нет объявлений!'

async def get_school(url):
	api = NetSchoolAPI(url)
	result = await api.schools()
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
