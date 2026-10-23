import json

import pytest

from opsgenie_google_calendar_sync.cli import authorize
from opsgenie_google_calendar_sync.config import Config


def test_authorize_persists_refresh_token_with_restrictive_mode(tmp_path):
    client = tmp_path / "oauth-client.json"
    client.write_text("{}")
    token = tmp_path / "token.json"
    config = Config("https://example.invalid/feed", "calendar", client, token)

    class Flow:
        @classmethod
        def from_client_secrets_file(cls, path, scopes):
            assert path == str(client)
            return cls()

        def run_local_server(self, **kwargs):
            return type("Credentials", (), {"to_json": lambda self: json.dumps({"refresh_token": "private"})})()

    authorize(config, flow_class=Flow)
    assert json.loads(token.read_text())["refresh_token"] == "private"
    assert token.stat().st_mode & 0o777 == 0o600


def test_failed_authorization_raises_sanitized_error(tmp_path):
    config = Config("https://example.invalid/feed", "calendar", tmp_path / "client", tmp_path / "token")

    class BrokenFlow:
        @classmethod
        def from_client_secrets_file(cls, *args):
            return cls()
        def run_local_server(self, **kwargs):
            raise RuntimeError("private oauth response")

    with pytest.raises(RuntimeError, match="authorization_failed") as exc:
        authorize(config, flow_class=BrokenFlow)
    assert "private oauth response" not in str(exc.value)
