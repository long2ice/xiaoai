import json
from hashlib import md5

import httpx
from xiaoai import constants


class XiaoAi:
    _common_params = {"sid": "micoapi", "_json": True}

    def __init__(self, user: str, password: str):
        self._user = user
        self._password = password

    def _parse_response(self, content: str):
        return json.loads(content.replace('&&&START&&&', ''))

    async def _get_login_sign(self):
        async with httpx.AsyncClient() as client:
            res = await client.get(
                constants.SERVICE_LOGIN_URL, params=self._common_params
            )
            ret = self._parse_response(res.text)
            return {'_sign': ret.get('_sign'), 'qs': ret.get('qs')}

    async def _service_auth(self, sign: dict):
        async with httpx.AsyncClient() as client:
            res = await client.post(
                constants.SERVICE_AUTH_URL, data={
                    'user': self._user,
                    'hash': md5(self._password.encode()).hexdigest(),
                    'callback': 'https://api.mina.mi.com/sts',
                    **self._common_params,
                    **sign
                },
                headers={

                }
            )
            ret = self._parse_response(res.text)
            return ret
