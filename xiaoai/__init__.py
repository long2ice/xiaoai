import base64
import json
from hashlib import md5, sha1
from typing import Any, Optional

import httpx

from xiaoai import utils
from xiaoai.exceptions import NeedLogin, ServiceAuthError


class XiaoAi:
    # url
    UBUS_URL = "https://api.mina.mi.com/remote/ubus"
    SERVICE_AUTH_URL = "https://account.xiaomi.com/pass/serviceLoginAuth2"
    SERVICE_LOGIN_URL = "https://account.xiaomi.com/pass/serviceLogin"
    PLAYLIST_URL = "https://api2.mina.mi.com/music/playlist/v2/lists"
    PLAYLIST_SONGS_URL = "https://api2.mina.mi.com/music/playlist/v2/songs"
    DEVICE_LIST_URL = "https://api.mina.mi.com/admin/v2/device_list"
    SONG_INFO_URL = "https://api2.mina.mi.com/music/song_info"
    # mock app device id
    APP_DEVICE_ID = "3C861A5820190429"
    SDK_VER = "3.4.1"
    APP_UA = "APP/com.xiaomi.mico APPV/2.1.17 iosPassportSDK/3.4.1 iOS/13.3.1"
    MINA_UA = "MISoundBox/2.1.17 (com.xiaomi.mico; build:2.1.55; iOS 13.3.1) Alamofire/4.8.2 MICO/iOSApp/appStore/2.1.17"

    _common_params = {"sid": "micoapi", "_json": True}
    _devices = None
    _current_device = None
    _is_login = False

    @property
    def is_login(self):
        return self._is_login

    def __init__(self, user: str, password: str):
        self._user = user
        self._password = password
        self.client = httpx.AsyncClient()

    def _parse_response(self, content: str):
        return json.loads(content.replace("&&&START&&&", ""))

    def _get_client_sign(self, nonce: str, ssecurity: str):
        s = f"nonce={nonce}&{ssecurity}"
        return base64.b64encode(sha1(s.encode()).digest()).decode()

    async def login(self):
        if self._is_login:
            return
        sign = await self._get_login_sign()
        auth_info = await self._service_auth(sign)
        await self._login_miai(auth_info)
        self._is_login = True

    async def _login_miai(self, auth_info: dict[str, Any]):
        nonce = auth_info.get("nonce", "")
        ssecurity = auth_info.get("ssecurity", "")
        location = auth_info.get("location", "")
        sign = self._get_client_sign(nonce, ssecurity)
        res = await self.client.get(location, params={"clientSign": sign})
        return res.json()

    async def _get_login_sign(self):
        res = await self.client.get(self.SERVICE_LOGIN_URL, params=self._common_params)
        ret = self._parse_response(res.text)
        return {"_sign": ret.get("_sign"), "qs": ret.get("qs")}

    async def _service_auth(self, sign: dict):
        res = await self.client.post(
            self.SERVICE_AUTH_URL,
            data={
                "user": self._user,
                "hash": md5(self._password.encode()).hexdigest().upper(),
                "callback": "https://api.mina.mi.com/sts",
                **self._common_params,
                **sign,
            },
            headers={"Cookie": f"deviceId={self.APP_DEVICE_ID};sdkVersion={self.SDK_VER}"},
        )
        ret = self._parse_response(res.text)
        if ret.get("code") != 0:
            raise ServiceAuthError(ret.get("desc"))
        return ret

    async def get_devices(self):
        if not self.is_login:
            raise NeedLogin()
        if self._devices:
            return
        params = {"master": 1}
        res = await self.client.get(self.DEVICE_LIST_URL, params=params)
        ret = res.json()
        self._devices = ret.get("data")
        self._current_device = self._devices[0]

    async def tts(self, text: str, device_id: Optional[str] = None):
        if not self.is_login:
            raise NeedLogin()
        if not device_id:
            device_id = self._current_device.get("deviceID")  # type: ignore
        url = self.UBUS_URL
        params = {
            "deviceId": device_id,
            "method": "text_to_speech",
            "path": "mibrain",
            "requestId": utils.generate_random_str(30),
            "message": json.dumps({"text": text}, ensure_ascii=False),
        }
        res = await self.client.post(url, params=params)
        ret = res.json()
        if ret.get("message") == "Success":
            return True
        return False
