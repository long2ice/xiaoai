import pytest

from conftest import xiaomi


@pytest.mark.dependency()
@pytest.mark.asyncio
async def test_get_devices():
    await xiaomi.get_devices()


@pytest.mark.dependency(depends=["test_get_devices"])
@pytest.mark.asyncio
async def test_tts():
    await xiaomi.tts("你好")
