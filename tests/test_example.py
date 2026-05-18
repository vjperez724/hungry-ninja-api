import pytest


def test_example():
    """Example test to verify pytest setup."""
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_async_example():
    """Example async test to verify pytest-asyncio setup."""
    result = 2 + 2
    assert result == 4
