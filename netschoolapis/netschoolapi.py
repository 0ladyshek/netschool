
from datetime import date, timedelta, datetime
from hashlib import md5
from io import BytesIO
from typing import Optional, Dict, List, Union

import httpx
from httpx import AsyncClient, Response

from . import errors, parser
import json

__all__ = ['NetSchoolAPI']


async def _die_on_bad_status(response: Response):
    response.raise_for_status()


class NetSchoolAPI:
    def __init__(self, url: str):
        url = url.rstrip('/')
        self._client = AsyncClient(
            base_url=f'{url}/',
            headers={'user-agent': 'NetSchoolAPI/5.0.3', 'referer': url},
            event_hooks={'response': [_die_on_bad_status]},
            verify = False,
        )

        self._student_id = -1
        self._year_id = -1
        self._school_id = -1
        self._class_id = -1
        self._school_name = None

        self._assignment_types: Dict[int, str] = {}
        self._login_data = ()

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def login(self, user_name: str, password: str, school: Union[str, int]):
        response_with_cookies = await self._client.get('webapi/logindata')
        self._client.cookies.extract_cookies(response_with_cookies)

        response = await self._client.post('webapi/auth/getdata')
        login_meta = response.json()
        salt = login_meta.pop('salt')
        self._ver = login_meta['ver']

        encoded_password = md5(
            password.encode('windows-1251')
        ).hexdigest().encode()
        pw2 = md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]

        try:
            response = await self._client.post(
                'webapi/login',
                data={
                    'loginType': 1,
                    **(await self._address(school)),
                    'un': user_name,
                    'pw': pw,
                    'pw2': pw2,
                    **login_meta,
                },
            )
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.CONFLICT:
                raise errors.AuthError("Incorrect username or password")
            else:
                raise http_status_error
        auth_result = response.json()

        if 'at' not in auth_result:
            raise errors.AuthError(auth_result['message'])

        self._client.headers['at'] = auth_result['at']
        self._at = auth_result['at']
        
        response = await self._client.get('webapi/student/diary/init')
        diary_info = response.json()
        student = diary_info['students'][diary_info['currentStudentId']]
        self._student_id = student['studentId']
        response = await self._client.get('webapi/years/current')
        year_reference = response.json()
        self._year_id = year_reference['id']

        response = await self._client.get(
            'webapi/grade/assignment/types', params={'all': False}
        )
        assignment_reference = response.json()
        self._assignment_types = {
            assignment['id']: assignment['name']
            for assignment in assignment_reference
        }
        self._login_data = (user_name, password, school)
        self._class_id = (await self.get_period())['filterSources'][1]['defaultValue']
        return student

    async def _request_with_optional_relogin(
            self, path: str, method="GET", params: dict = None,
            json: dict = None, data: dict = None):
        try:
            response = await self._client.request(
                method, path, params=params, json=json, data=data
            )
        except httpx.HTTPStatusError as http_status_error:
            if (
                http_status_error.response.status_code
                == httpx.codes.UNAUTHORIZED
            ):
                if self._login_data:
                    await self.login(*self._login_data)
                    return await self._client.request(
                        method, path, params=params, json=json, data=data
                    )
                else:
                    raise errors.AuthError(
                        ".login() before making requests that need "
                        "authorization"
                    )
            else:
                raise http_status_error
        else:
            return response

    async def download_attachment_as_bytes(
            self, attachment: str,
        ):
        return (await self._client.get(f'webapi/attachments/{attachment["id"]}')).content

    async def diary(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> dict:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._request_with_optional_relogin(
            'webapi/student/diary',
            params={
                'studentId': self._student_id,
                'yearId': self._year_id,
                'weekStart': start.isoformat(),
                'weekEnd': end.isoformat(),
            },
        )
        return response.json()

    async def overdue(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[dict]:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._request_with_optional_relogin(
            'webapi/student/diary/pastMandatory',
            params={
                'studentId': self._student_id,
                'yearId': self._year_id,
                'weekStart': start.isoformat(),
                'weekEnd': end.isoformat(),
            },
        )
        return response.json()

    async def announcements(
            self, take: Optional[int] = -1) -> List[dict]:
        response = await self._request_with_optional_relogin(
            'webapi/announcements', params={'take': take}
        )
        return response.json()

    async def attachments(
            self, assignment: str) -> List[dict]:
        response = await self._request_with_optional_relogin(
            method="POST",
            path='webapi/student/diary/get-attachments',
            params={'studentId': self._student_id},
            json={'assignId': [assignment.id]},
        )
        return response.json()

    async def school(self, school: Optional[int] = None):
        if not school:
            school = self._school_id
        response = await self._request_with_optional_relogin(
            'webapi/schools/{0}/card'.format(school)
        )
        return response.json()

    async def schools(self):
        try:
            response = await self._client.get(
                'webapi/addresses/schools', params={'funcType': 2}
            )
            response.raise_for_status()
            schools_reference = response.json()
        except httpx.HTTPError:
            response = await self._client.get(
                'webapi/prepareloginform'
            )
            schools_reference = response.json()['schools']
        return schools_reference

    async def birthdayMonth(self, period: Optional[date] = datetime.now(), student: Optional[bool] = True, parent: Optional[bool] = True, staff: Optional[bool] = True):
        response = await self._request_with_optional_relogin(
            'asp/Calendar/MonthBirth.asp', method='POST',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'Year': period.year,
                'Month': period.month,
                'ViewType': '1',
                'LoginType': '0',
                'BIRTH_STAFF': 1 if staff else 0,
                'BIRTH_PARENT': 4 if parent else 0,
                'BIRTH_STUDENT': 2 if student else 0,
                'MonthYear': f'{period.month},{period.year}',
            }
        )
        '''
        response = parser.parseBirthDay(response.text)
        users = schemas.BirthDayUser().load(response, many=True)
        return [data.BirthDayUser(**user) for user in users]
        '''
        return parser.parseBirthDay(response.text)

    async def holidayMonth(self, period: Optional[date] = datetime.now()):
        response = await self._client.post(
            'asp/Calendar/MonthViewS.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'Year': period.year,
                'Month': period.month,
                'ViewType': '1',
                'LoginType': '0',
                'MonthYear': f'{period.month},{period.year}',
            }
        )
        return parser.parseHolidayMonth(response.text)

    async def activeSessions(self):
        response = await self._client.get(
            'webapi/context/activeSessions'
        )
        '''
        sessions = schemas.Session().load(response.json(), many=True)
        return [data.Session(**session) for session in sessions]
        '''
        return response.json()

    async def get_period(self):
        response = await self._client.get(
            'webapi/reports/studenttotal'
        )
        return response.json()
    
    async def userPhoto(self):
        response_with_cookies = await self._client.get(
            'asp/MySettings/MySettings.asp',
            params={
                'AT': self._at
            })
        self._client.cookies.extract_cookies(response_with_cookies)

        try:
            response = await self._client.get(
                'webapi/users/photo',
                params={
                    'AT': self._at,
                    'userId': self._student_id,
                })
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == 301:
                response = await self._client.get(
                    'images/common/photono.jpg'
                )
            else:
                raise http_status_error
        return response

    async def userInfo(self):
        response = await self._client.post(
            'asp/MySettings/MySettings.asp',
            params = {
                'AT': self._at,
            },
            data = {
                'at': self._at,
                'VER': self._ver,
                'UID': self._student_id,
            },
        )
        return parser.parseUserInfo(response.text)

    
    async def totalMarks(self):
        response_with_cookies = await self._client.post(
            'asp/Reports/ReportStudentTotalMarks.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'RPNAME': 'Итоговые отметки',
                'RPTID': 'StudentTotalMarks',
            })
        self._client.cookies.extract_cookies(response_with_cookies)
        response = await self._client.post(
            'asp/Reports/StudentTotalMarks.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'LoginType': '0',
                'RPTID' :'StudentTotalMarks',
                'SID': self._student_id,
            }
        )
        return response.text

    async def parentReport(self, term: Optional[int] = 1):
        response_with_cookies = await self._client.post(
            'asp/Reports/ReportParentInfoLetter.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'RPNAME': 'Информационное письмо для родителей',
                'RPTID': 'ParentInfoLetter',
            })
        self._client.cookies.extract_cookies(response_with_cookies)

        response = await self._client.post(
            'asp/Reports/ParentInfoLetter.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'LoginType': '0',
                'RPTID' :'ParentInfoLetter',
                'SID': self._student_id,
                'ReportType': 2,
                'PCLID': self._class_id,
                'TERMID': ((await self.getTermId())[term - 1]),
            })
        return parser.parseReportParent(response.text)

    async def getTermId(self):
        response = await self._client.post(
            'asp/Reports/ReportParentInfoLetter.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'RPNAME': 'Информационное письмо для родителей',
                'RPTID': 'ParentInfoLetter',
            })
        return parser.parseTermId(response.text)

    async def reportTotal(self):
        response_with_cookies = await self._client.post(
            'asp/Reports/ReportStudentTotalMarks.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'RPNAME': 'Итоговые отметки',
                'RPTID': 'StudentTotalMarks',
            })
        self._client.cookies.extract_cookies(response_with_cookies)

        response = await self._client.post(
            'asp/Reports/StudentTotalMarks.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'LoginType': '0',
                'RPTID' :'StudentTotalMarks',
                'SID': self._student_id,
            })
        return parser.parseReportTotal(response.text)

    async def setYear(self, year_id: Optional[int] = None):
        year_id = self._year_id if not year_id else year_id
        await self._client.post(
            'asp/MySettings/SaveParentSettings.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'UID': self._student_id,
                'CURRYEAR': year_id,
            })
        response = await self._client.get('webapi/years/current')
        year_reference = response.json()
        self._year_id = year_reference['id']
        return year_reference['id']

    async def reportAverageMark(self):
        response_with_cookies = await self._client.post(
            'asp/Reports/ReportStudentAverageMark.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'RPNAME': 'Cредний балл',
                'RPTID': 'StudentAverageMark',
            })
        self._client.cookies.extract_cookies(response_with_cookies)

        period = await self.get_period()
        period = period['filterSources'][2]['defaultValue'].split(' - ')
        start = datetime.strptime(period[0], '%Y-%m-%dT%H:%M:%S.0000000')
        end = datetime.strptime(period[1], '%Y-%m-%dT%H:%M:%S.0000000')
        response = await self._client.post(
            'asp/Reports/StudentAverageMark.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
                'LoginType': '0',
                'RPTID' :'StudentAverageMark',
                'SID': self._student_id,
                'ADT': f"{start.day}.{start.month}.{start.year}",
                'DDT': f"{end.day}.{end.month}.{end.year}",
            })
        return parser.parseAverageMark(response.text)

    async def yearView(self):
        response = await self._client.post(
            'asp/SetupSchool/Calendar/YearView.asp',
            data = {
                'AT': self._at,
                'VER': self._ver,
            }
        )
        return parser.parseYearView(response.text)

    async def reportFile(self, start: Optional[datetime] = None, end: Optional[datetime] = None):
        start = start.isoformat(sep='T')
        end  = end.isoformat(sep='T')
        period = f'{start} - {end}'
        response = await self._client.get(
            'WebApi/signalr/negotiate',
            params = {
                '_': self._ver,
                'at': self._at,
                'clientProtocol': '1.5',
                'transport': 'webSockets',
            })
        connectToken = response.json()['ConnectionToken']
        async with self._client.stream('GET',
                                        'WebApi/signalr/connect',
                                        timeout = 20,
                                        params = {
                                            'transport': 'serverSentEvents',
                                            'clientProtocol': '1.5',
                                            'at': self._at,
                                            'connectionToken': connectToken,
                                            'connectionData': '[{"name":"queuehub"}]',
                                            'tid': '8',
                                        }) as r:
            async for chunk in r.aiter_text():
                if 'initialized' in chunk:
                    await self._client.get(
                        'WebApi/signalr/start',
                        params = {
                            'transport': 'serverSentEvents',
                            'clientProtocol': '1.5',
                            'at': self._at,
                            'connectionToken': connectToken,
                            'connectionData': '[{"name":"queuehub"}]',
                            '_': self._ver,
                        })

                    selectedData = (await self.get_period())['filterSources']
                    await self._client.post(
                        'webapi/reports/studenttotal/queue',
                        json = {
                            "selectedData": 
                                [{            
                                    "filterId":"SID",
                                    "filterValue":  selectedData[0]['defaultValue'],
                                },{
                                    "filterId":"PCLID",
                                    "filterValue": selectedData[1]['defaultValue']
                                }, {
                                    "filterId":"period",
                                    "filterValue": selectedData[2]['defaultValue'] if not period else period
                                }],
                            "params":
                                [{
                                    "name":"SCHOOLYEARID",
                                    "value": self._year_id,
                                },{
                                    "name":"SERVERTIMEZONE",
                                    "value":0,
                                },{
                                    "name":"FULLSCHOOLNAME",
                                    "value": self._school_name
                                },{
                                    "name":"DATEFORMAT",
                                    "value":"d\u0001mm\u0001yy\u0001."
                                }]
                        }
                    )

                    await self._client.post(
                        'WebApi/signalr/send',
                        params = {
                            'transport': 'serverSentEvents',
                            'clientProtocol': '1.5',
                            'at': self._at,
                            'connectionToken': connectToken,
                            'connectionData': '[{"name":"queuehub"}]',
                        },
                        data = {
                            'data': {"H":"queuehub","M":"StartTask","A":[1967575],"I":0}
                        }
                    )
                else:
                    chunk = json.loads(chunk.replace('data: ', ''))
                    if chunk:
                        if chunk['M']:
                            if chunk['M'][0]['M'] == 'complete':
                                await self._client.post(
                                    'WebApi/signalr/abort',
                                    params = {
                                        'transport': 'serverSentEvents',
                                        'clientProtocol': '1.5',
                                        'at': self._at,
                                        'connectionToken': connectToken,
                                        'connectionData': '[{"name":"queuehub"}]',
                                    }
                                )
                                file_id = chunk['M'][0]['A'][0]['Data']
                                file = await self._client.get(
                                    f'webapi/files/{file_id}'
                                )
                                #return parser.parseReportFile(file.text)
                                return file.text

    async def logout(self):
        await self._client.post('webapi/auth/logout')
        await self._client.aclose()

    async def close(self):
        await self._client.aclose()

    async def _address(self, school: Union[str, int]) -> Dict[str, int]:
        try:
            response = await self._client.get(
                'webapi/addresses/schools', params={'funcType': 2}
            )
            response.raise_for_status()
            schools_reference = response.json()
            for school_ in schools_reference:
                if school_['name'] == school or school_['id'] == school:
                    self._school_id = school_['id']
                    self._school_name = school_['name']
                    return {
                        'cid': school_['countryId'],
                        'sid': school_['stateId'],
                        'pid': school_['municipalityDistrictId'],
                        'cn': school_['cityId'],
                        'sft': 2,
                        'scid': school_['id'],
                    }
        except httpx.HTTPError:
            response = await self._client.get(
                'webapi/prepareloginform'
            )
            schools_reference = response.json()['schools']
            for school_ in schools_reference:
                if school_['name'] == school or school_['id'] == school:
                    self._school_id = school_['id']
                    self._school_name = school_['name']
                    return {
                        'sft': 2,
                        'scid': school_['id'],
                    }
        
        raise errors.SchoolNotFoundError(school)
