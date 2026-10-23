from datetime import datetime, timezone
from datetime import timedelta

from google.oauth2.credentials import Credentials

from opsgenie_google_calendar_sync.cli import authorize, sync_once
from opsgenie_google_calendar_sync.config import Config
from opsgenie_google_calendar_sync.opsgenie_ical import Shift


def test_thirty_scheduled_syncs_do_not_request_interactive_auth(tmp_path, monkeypatch):
    config = Config("https://example.invalid/feed", "calendar", tmp_path / "client", tmp_path / "token")
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.fetch_feed", lambda url: b"synthetic")
    shift = Shift("uid", datetime(2030, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, 1, tzinfo=timezone.utc))
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.parse_feed", lambda payload: [shift])
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.load_credentials", lambda path, scopes: object())
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.build_calendar_service", lambda credentials: object())

    class Gateway:
        def __init__(self, *args): pass
        def list_managed_events(self, marker): return []
        def create_event(self, event): pass

    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.GoogleCalendarGateway", Gateway)
    results = [sync_once(config) for _ in range(30)]
    assert all(result.outcome == "success" for result in results)


def test_one_authorization_persists_token_for_thirty_noninteractive_runs(tmp_path, monkeypatch):
    config = Config("https://example.invalid/feed", "calendar", tmp_path / "client.json", tmp_path / "token.json")
    token = Credentials(
        token="access-token",
        refresh_token="refresh-token",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client-id",
        client_secret="client-secret",
        scopes=["https://www.googleapis.com/auth/calendar.events"],
        expiry=datetime.now(timezone.utc) + timedelta(days=1),
    )

    class Flow:
        calls = 0
        @classmethod
        def from_client_secrets_file(cls, *args):
            cls.calls += 1
            return cls()
        def run_local_server(self, **kwargs):
            return token

    authorize(config, flow_class=Flow)
    assert Flow.calls == 1
    assert "refresh-token" in config.oauth_token_file.read_text()

    shift = Shift("uid", datetime.now(timezone.utc) + timedelta(days=1), datetime.now(timezone.utc) + timedelta(days=1, hours=1))
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.fetch_feed", lambda url: b"synthetic")
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.parse_feed", lambda payload: [shift])
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.build_calendar_service", lambda credentials: credentials)

    class Gateway:
        def __init__(self, service, calendar_id):
            assert service.refresh_token == "refresh-token"
        def list_managed_events(self, marker): return []
        def create_event(self, event): pass

    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.GoogleCalendarGateway", Gateway)
    results = [sync_once(config) for _ in range(30)]
    assert all(result.outcome == "success" for result in results)
