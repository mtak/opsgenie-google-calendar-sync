import pytest

from oncall_calendar_sync.cli import sync_once
from oncall_calendar_sync.config import Config


INVALID_EVENTS = [
    "DTSTART:20300101T000000Z\nDTEND:20300101T010000Z",  # missing UID
    "UID:duplicate\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\n"
    "END:VEVENT\nBEGIN:VEVENT\nUID:duplicate\nDTSTART:20300102T000000Z\nDTEND:20300102T010000Z",
    "UID:recurring\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nRRULE:FREQ=DAILY",
    "UID:cancelled\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nSTATUS:CANCELLED",
    "UID:missing-end\nDTSTART:20300101T000000Z",
    "UID:missing-start\nDTEND:20300101T010000Z",
    "UID:date-only\nDTSTART;VALUE=DATE:20300101\nDTEND;VALUE=DATE:20300102",
]
INVALID_PAYLOADS = [b"", b"not ical", b"BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"] + [
    (
        "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\n"
        + event
        + "\nEND:VEVENT\nEND:VCALENDAR"
    ).encode()
    for event in INVALID_EVENTS
]


@pytest.mark.parametrize("payload", INVALID_PAYLOADS)
def test_invalid_source_causes_zero_destination_access(tmp_path, monkeypatch, payload):
    config = Config("https://private.invalid/feed", "private-calendar", tmp_path / "client", tmp_path / "token")
    monkeypatch.setattr("oncall_calendar_sync.cli.fetch_feed", lambda url: payload)
    monkeypatch.setattr("oncall_calendar_sync.cli.load_credentials", lambda *args: pytest.fail("credentials loaded before source validation"))
    outcome = sync_once(config)
    assert outcome.outcome == "failure"
    assert outcome.error_category.startswith("source_")
