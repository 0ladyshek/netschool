from datetime import date, timedelta, datetime
from hashlib import md5
from io import BytesIO
from typing import Optional, Dict, List, Union

import httpx
from httpx import AsyncClient, Response

from . import errors, parser
#from netschoolapi import parser

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
        )

        self._student_id = -1
        self._year_id = -1
        self._school_id = -1

        self._assignment_types: Dict[int, str] = {}
        self._login_data = ()

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def login(self, user_name: str, password: str, school: [str or int]):
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
        return student

    async def _request_with_optional_relogin(
            self, path: str, method="GET", params: dict = None,
            json: dict = None):
        try:
            response = await self._client.request(
                method, path, params=params, json=json
            )
        except httpx.HTTPStatusError as http_status_error:
            if (
                http_status_error.response.status_code
                == httpx.codes.UNAUTHORIZED
            ):
                if self._login_data:
                    await self.login(*self._login_data)
                    return await self._client.request(
                        method, path, params=params, json=json
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

    async def download_attachment(
            self, attachment: str,
            path_or_file: Union[BytesIO, str] = None):
        """
        If `path_to_file` is a string, it should contain absolute path to file
        """
        if path_or_file is None:
            file = open(attachment.name, "wb")
        elif isinstance(path_or_file, str):
            file = open(path_or_file, "wb")
        else:
            file = path_or_file
        file.write((
            await self._request_with_optional_relogin(
                f"webapi/attachments/{attachment.id}"
            )
        ).content)

    async def download_attachment_as_bytes(
            self, attachment: str) -> BytesIO:
        attachment_contents_buffer = BytesIO()
        await self.download_attachment(
            attachment, path_or_file=attachment_contents_buffer
        )
        return attachment_contents_buffer

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

    async def school(self):
        response = await self._request_with_optional_relogin(
            'webapi/schools/{0}/card'.format(self._school_id)
        )
        return response.json()

    async def schools(self):
        response = await self._client.get(
            'webapi/addresses/schools', params={'funcType': 2}
        )
        return response.json()
    
    async def birthdayMonth(self, period: Optional[date] = datetime.now(), student: Optional[bool] = True, parent: Optional[bool] = True, staff: Optional[bool] = True):
        response = await self._client.post(
            'asp/Calendar/MonthBirth.asp',
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
        return parser.parseBirthDay(response.text)

    async def get_period(self):
        response = await self._client.get(
            'webapi/reports/studenttotal'
        )
        return response.json()
    
    async def logout(self):
        await self._client.post('webapi/auth/logout')
        await self._client.aclose()

    async def _address(self, school: [str or int]) -> Dict[str, int]:
        response = await self._client.get(
            'webapi/addresses/schools', params={'funcType': 2}
        )

        schools_reference = response.json()
        for school_ in schools_reference:
            if school_['name'] == school or school_['id'] == school:
                self._school_id = school_['id']
                return {
                    'cid': school_['countryId'],
                    'sid': school_['stateId'],
                    'pid': school_['municipalityDistrictId'],
                    'cn': school_['cityId'],
                    'sft': 2,
                    'scid': school_['id'],
                }
        raise errors.SchoolNotFoundError(school)
