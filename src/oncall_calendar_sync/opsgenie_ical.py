"""Fetch and validate an iCalendar source snapshot before any writes."""

from dataclasses import dataclass
from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

from icalendar import Calendar


class FeedError(Exception):
    """The source could not be retrieved or safely interpreted."""


@dataclass(frozen=True)
class Shift:
    uid: str
    start: datetime
    end: datetime
    summary: str = ""
    description: str = ""
    location: str = ""


def fetch_feed(url: str, timeout: float = 30) -> bytes:
    try:
        request = Request(url, headers={"User-Agent": "oncall-calendar-sync/0.1"})
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise FeedError("source_fetch_failed")
            return response.read()
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise FeedError("source_fetch_failed") from exc


def parse_feed(payload: bytes) -> list[Shift]:
    if not payload or not payload.strip():
        raise FeedError("source_empty")
    try:
        calendar = Calendar.from_ical(payload)
    except Exception as exc:
        raise FeedError("source_malformed") from exc
    if calendar.name != "VCALENDAR":
        raise FeedError("source_unsupported")

    shifts, seen = [], set()
    try:
        for component in calendar.walk("VEVENT"):
            if component.get("STATUS", "CONFIRMED").upper() == "CANCELLED":
                raise FeedError("source_unsupported")
            uid = str(component.get("UID", "")).strip()
            if not uid or uid in seen:
                raise FeedError("source_identity_invalid")
            seen.add(uid)
            recurrence_fields = ("RRULE", "RDATE", "EXRULE", "EXDATE", "RECURRENCE-ID")
            if any(component.get(field) is not None for field in recurrence_fields):
                raise FeedError("source_unsupported")
            start, end = component.decoded("DTSTART"), component.decoded("DTEND")
            if not isinstance(start, datetime) or not isinstance(end, datetime):
                raise FeedError("source_unsupported")
            if start.tzinfo is None or end.tzinfo is None or end <= start:
                raise FeedError("source_time_invalid")
            shifts.append(Shift(uid, start, end, str(component.get("SUMMARY", "")), str(component.get("DESCRIPTION", "")), str(component.get("LOCATION", ""))))
    except FeedError:
        raise
    except Exception as exc:
        raise FeedError("source_malformed") from exc
    if not shifts:
        raise FeedError("source_empty")
    return shifts
