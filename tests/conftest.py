import json
import os
import urllib.request

import pytest
from fastapi.testclient import TestClient

# Dummy config so the app can be imported/started without real external
# services. Only set if not already provided (e.g. via a local .env).
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("LLM_MODEL", "test")  # pydantic-ai's built-in TestModel
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("AUTH0_CLIENT_ID", "test-client-id")
os.environ.setdefault("AUTH0_DOMAIN", "test.auth0.com")
os.environ.setdefault("AUTH0_AUDIENCE", "test-audience")

_real_urlopen = urllib.request.urlopen


def _fake_urlopen(url, *args, **kwargs):
    # Auth0 setup fetches this at import time; fake it out so tests don't
    # need real network access or a live Auth0 tenant.
    target = url.full_url if isinstance(url, urllib.request.Request) else url
    if "/.well-known/jwks.json" in target:
        return _FakeJwksResponse()
    return _real_urlopen(url, *args, **kwargs)


class _FakeJwksResponse:
    def read(self):
        return json.dumps({"keys": []}).encode()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


urllib.request.urlopen = _fake_urlopen


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
