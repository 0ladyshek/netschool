from bs4 import BeautifulSoup as bs4
from typing import List

def parseBirthDay(birthDay: str) -> List:
	births_dict = []
	html = bs4(birthDay, 'lxml')
	births = html.find_all('tr')
	for people in births[1:]:
		atributs = people.find_all('td')
		births_dict.append({'class': atributs[0].text, 'role': atributs[1].text, 'date': atributs[2].text, 'name': atributs[3].text})
	return births_dict
