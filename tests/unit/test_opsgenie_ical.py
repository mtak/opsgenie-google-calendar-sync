from datetime import timezone

import pytest

from opsgenie_google_calendar_sync.opsgenie_ical import FeedError, parse_feed


def test_parses_event_fields_and_timezone():
    events = parse_feed((__import__("pathlib").Path(__file__).parents[1] / "fixtures/shifts.ics").read_bytes())
    assert len(events) == 1
    assert events[0].uid == "shift-1"
    assert events[0].summary == "Primary on-call"
    assert events[0].start.utcoffset() is not None
    assert events[0].start.utcoffset().total_seconds() == 3600
    assert events[0].end.utcoffset().total_seconds() == 7200
    assert (events[0].end.astimezone(timezone.utc) - events[0].start.astimezone(timezone.utc)).total_seconds() == 3600


@pytest.mark.parametrize("payload", [b"", b"garbage", b"BEGIN:VCALENDAR\nEND:VCALENDAR"])
def test_rejects_empty_or_malformed_feeds(payload):
    with pytest.raises(FeedError):
        parse_feed(payload)


def test_rejects_missing_duplicate_uid_and_invalid_interval():
    with pytest.raises(FeedError):
        parse_feed(b"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nEND:VEVENT\nEND:VCALENDAR")
    with pytest.raises(FeedError):
        parse_feed(b"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nUID:zero\nDTSTART:20300101T000000Z\nDTEND:20300101T000000Z\nEND:VEVENT\nEND:VCALENDAR")


def test_rejects_duplicate_uid():
    payload = b"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nUID:same\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nEND:VEVENT\nBEGIN:VEVENT\nUID:same\nDTSTART:20300102T000000Z\nDTEND:20300102T010000Z\nEND:VEVENT\nEND:VCALENDAR"
    with pytest.raises(FeedError):
        parse_feed(payload)


@pytest.mark.parametrize(
    "event",
    [
        "UID:recurring\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nRRULE:FREQ=DAILY",
        "UID:rdate\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nRDATE:20300102T000000Z",
        "UID:exrule\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nEXRULE:FREQ=DAILY",
        "UID:exdate\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nEXDATE:20300102T000000Z",
        "UID:recurrence-instance\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nRECURRENCE-ID:20300101T000000Z",
        "UID:cancelled\nDTSTART:20300101T000000Z\nDTEND:20300101T010000Z\nSTATUS:CANCELLED",
        "UID:missing-start\nDTEND:20300101T010000Z",
        "UID:missing-end\nDTSTART:20300101T000000Z",
        "UID:date-only\nDTSTART;VALUE=DATE:20300101\nDTEND;VALUE=DATE:20300102",
    ],
)
def test_rejects_unsupported_or_incomplete_event_shapes(event):
    payload = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\n{event}\nEND:VEVENT\nEND:VCALENDAR".encode()
    with pytest.raises(FeedError):
        parse_feed(payload)
