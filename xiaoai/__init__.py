import base64
import json
from hashlib import md5, sha1

import httpx
from xiaoai import constants
from xiaoai.exceptions import ServiceAuthError


class XiaoAi:
    _common_params = {"sid": "micoapi", "_json": True}

    def __init__(self, user: str, password: str):
        self._user = user
        self._password = password

    def _parse_response(self, content: str):
        return json.loads(content.replace('&&&START&&&', ''))

    def _get_client_sign(self, nonce: str, ssecurity: str):
        s = f'nonce={nonce}&{ssecurity}'
        return base64.b64encode(sha1(s.encode()).digest())

    async def login_miai(self, auth_info: dict):
        nonce = auth_info.get('nonce')
        ssecurity = auth_info.get('ssecurity')
        location = auth_info.get('location')
        sign = self._get_client_sign(nonce, ssecurity)
        async with httpx.AsyncClient() as client:
            res = await client.get(location, params={
                'clientSign': sign
            })

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
                    'hash': md5(self._password.encode()).hexdigest().upper(),
                    'callback': 'https://api.mina.mi.com/sts',
                    **self._common_params,
                    **sign
                },
                headers={
                    'Cookie': f'deviceId={constants.APP_DEVICE_ID};sdkVersion={constants.SDK_VER}'
                }
            )
            ret = self._parse_response(res.text)
            if ret.get('code') != 0:
                raise ServiceAuthError(ret.get('desc'))
            return ret
