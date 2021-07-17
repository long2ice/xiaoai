import asyncio
import os

import pytest

from xiaoai import XiaoAi

xiaomi = XiaoAi(user=os.getenv("XIAOAI_USER", ""), password=os.getenv("XIAOAI_PASSWORD", ""))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def login():
    ret = await xiaomi.login()
    return ret
