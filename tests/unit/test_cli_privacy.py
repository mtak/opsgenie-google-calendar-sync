from datetime import datetime, timezone

from opsgenie_google_calendar_sync.cli import _report, sync_once
from opsgenie_google_calendar_sync.config import Config
from opsgenie_google_calendar_sync.opsgenie_ical import Shift


def test_failure_output_excludes_private_values(tmp_path, monkeypatch, capsys):
    secret_url = "https://private.invalid/secret-feed"
    secret_calendar = "calendar-secret"
    config = Config(secret_url, secret_calendar, tmp_path / "client", tmp_path / "token")
    shift = Shift("private-event-title", datetime(2030, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, 1, tzinfo=timezone.utc), "private-event-title")
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.fetch_feed", lambda url: b"synthetic")
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.parse_feed", lambda payload: [shift])
    monkeypatch.setattr("opsgenie_google_calendar_sync.cli.load_credentials", lambda *args: (_ for _ in ()).throw(RuntimeError("oauth-token-secret")))
    _report(sync_once(config))
    captured = capsys.readouterr()
    output = captured.out + captured.err
    for secret in (secret_url, secret_calendar, "private-event-title", "oauth-token-secret"):
        assert secret not in output
