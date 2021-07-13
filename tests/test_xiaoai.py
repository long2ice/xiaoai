import os
import pytest
from xiaoai import XiaoAi

xiaomi = XiaoAi(
    username=os.getenv("XIAOAI_USERNAME"), password=os.getenv("XIAOAI_PASSWORD")
)


@pytest.mark.asyncio
async def test_get_login_sign():
    ret = await xiaomi._get_login_sign()
    print(ret)
