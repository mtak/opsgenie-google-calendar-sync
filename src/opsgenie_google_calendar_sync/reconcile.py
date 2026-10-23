"""Idempotent, ownership-scoped reconciliation of source shifts."""

from dataclasses import dataclass
from datetime import datetime, timezone

from .opsgenie_ical import Shift

SYNC_MARKER = "opsgenie-calendar-sync-v1"


@dataclass(frozen=True)
class ReconcileResult:
    added: int = 0
    updated: int = 0
    removed: int = 0
    failed: bool = False
    error_category: str = ""


def _date_time(value: datetime) -> dict:
    result = {"dateTime": value.isoformat()}
    zone = getattr(value.tzinfo, "key", None) or getattr(value.tzinfo, "zone", None)
    if zone:
        result["timeZone"] = zone
    return result


def _body(shift: Shift, marker: str) -> dict:
    return {
        "summary": shift.summary,
        "description": shift.description,
        "location": shift.location,
        "start": _date_time(shift.start),
        "end": _date_time(shift.end),
        "extendedProperties": {"private": {"oncallCalendarSync": marker, "sourceUid": shift.uid}},
    }


def _comparable(event: dict) -> tuple:
    times = []
    for key in ("start", "end"):
        time_object = event.get(key, {})
        value = time_object.get("dateTime", "")
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except (AttributeError, ValueError):
            pass
        times.append((value, time_object.get("timeZone", "")))
    return tuple(event.get(key, "") for key in ("summary", "description", "location")) + tuple(times)


def reconcile(source_events, gateway, marker: str = SYNC_MARKER, now: datetime | None = None) -> ReconcileResult:
    try:
        shifts = [event if isinstance(event, Shift) else Shift(event["uid"], event["start"], event["end"], event.get("summary", ""), event.get("description", ""), event.get("location", "")) for event in source_events]
    except (KeyError, TypeError):
        return ReconcileResult(failed=True, error_category="source_validation")
    if not shifts:
        return ReconcileResult(failed=True, error_category="source_empty")
    uids = [shift.uid for shift in shifts]
    if any(not uid for uid in uids) or len(uids) != len(set(uids)):
        return ReconcileResult(failed=True, error_category="source_validation")
    if any(shift.start.tzinfo is None or shift.end.tzinfo is None or shift.end <= shift.start for shift in shifts):
        return ReconcileResult(failed=True, error_category="source_validation")
    try:
        existing = gateway.list_managed_events(marker)
    except Exception:
        return ReconcileResult(failed=True, error_category="calendar_read")

    by_uid = {}
    managed = []
    for event in existing:
        properties = event.get("extendedProperties", {}).get("private", {})
        if properties.get("oncallCalendarSync") != marker:
            continue
        if not event.get("id") or not _event_end(event):
            return ReconcileResult(failed=True, error_category="managed_event_invalid")
        managed.append(event)
        uid = properties.get("sourceUid")
        if uid:
            if uid in by_uid:
                return ReconcileResult(failed=True, error_category="managed_identity_ambiguous")
            by_uid[uid] = event

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    matched = {}
    used = set()
    # Prefer exact source UID matches, then match unchanged event details to
    # absorb Opsgenie's schedule-wide UID rotation without calendar churn.
    for shift in shifts:
        previous = by_uid.get(shift.uid)
        if previous is not None:
            matched[shift.uid] = previous
            used.add(id(previous))
    for shift in shifts:
        if shift.uid in matched or shift.end.astimezone(timezone.utc) <= current:
            continue
        desired = _body(shift, marker)
        candidates = [event for event in managed if id(event) not in used and _comparable(event) == _comparable(desired)]
        if len(candidates) > 1:
            return ReconcileResult(failed=True, error_category="managed_identity_ambiguous")
        if candidates:
            matched[shift.uid] = candidates[0]
            used.add(id(candidates[0]))

    added = updated = removed = 0
    try:
        for shift in shifts:
            if shift.end.astimezone(timezone.utc) <= current:
                continue
            desired = _body(shift, marker)
            previous = matched.get(shift.uid)
            if previous is None:
                gateway.create_event(desired)
                added += 1
            elif _event_ended(previous, current):
                continue
            elif (
                _comparable(previous) != _comparable(desired)
                or previous.get("extendedProperties", {}).get("private", {}).get("sourceUid") != shift.uid
            ):
                gateway.update_event(previous["id"], {**previous, **desired})
                updated += 1
        for event in managed:
            if id(event) not in used and not _event_ended(event, current):
                gateway.delete_event(event["id"])
                removed += 1
    except Exception:
        return ReconcileResult(added, updated, removed, failed=True, error_category="calendar_write")
    return ReconcileResult(added, updated, removed)


def _event_ended(event: dict, current: datetime) -> bool:
    try:
        end = event["end"]["dateTime"].replace("Z", "+00:00")
        return datetime.fromisoformat(end).astimezone(timezone.utc) <= current
    except (KeyError, AttributeError, ValueError):
        return False


def _event_end(event: dict) -> datetime | None:
    try:
        value = event["end"]["dateTime"]
        end = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return end.astimezone(timezone.utc) if end.tzinfo else None
    except (KeyError, AttributeError, TypeError, ValueError):
        return None
