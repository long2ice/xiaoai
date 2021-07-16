import os

import pytest

from xiaoai import XiaoAi

xiaomi = XiaoAi(user=os.getenv("XIAOAI_USER"), password=os.getenv("XIAOAI_PASSWORD"))


@pytest.mark.asyncio
@pytest.fixture
async def test_get_login_sign():
    ret = await xiaomi._get_login_sign()
    return ret


@pytest.mark.asyncio
@pytest.fixture
async def test_service_auth(test_get_login_sign):
    ret = await xiaomi._service_auth(test_get_login_sign)
    assert "qs" in ret
    assert "ssecurity" in ret
    return ret


@pytest.mark.asyncio
async def test_login_miai(test_service_auth):
    await xiaomi.login_miai(test_service_auth)
