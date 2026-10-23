"""Opt-in smoke test; requires a dedicated disposable test calendar."""

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from oncall_calendar_sync.config import load_config
from oncall_calendar_sync.google_calendar import GoogleCalendarGateway, build_calendar_service, load_credentials
from oncall_calendar_sync.opsgenie_ical import Shift
from oncall_calendar_sync.reconcile import reconcile


@pytest.mark.skipif(os.getenv("ONCALL_SYNC_INTEGRATION") != "1", reason="opt-in dedicated Calendar API test")
def test_authorized_create_update_delete_on_dedicated_calendar():
    config = load_config()
    if not os.getenv("ONCALL_SYNC_TEST_CALENDAR_ID") or config.target_calendar_id != os.getenv("ONCALL_SYNC_TEST_CALENDAR_ID"):
        pytest.fail("target must match ONCALL_SYNC_TEST_CALENDAR_ID")
    gateway = GoogleCalendarGateway(build_calendar_service(load_credentials(config.oauth_token_file, ["https://www.googleapis.com/auth/calendar.events"])), config.target_calendar_id)
    marker = f"integration-{uuid.uuid4()}"
    body = {"summary": "Temporary sync integration event", "start": {"dateTime": "2030-01-01T09:00:00Z"}, "end": {"dateTime": "2030-01-01T10:00:00Z"}, "extendedProperties": {"private": {"oncallCalendarSync": marker, "sourceUid": marker}}}
    created = gateway.create_event(body)
    try:
        updated = {**body, "summary": "Updated temporary sync integration event"}
        gateway.update_event(created["id"], updated)
    finally:
        gateway.delete_event(created["id"])


@pytest.mark.skipif(os.getenv("ONCALL_SYNC_INTEGRATION") != "1", reason="opt-in dedicated Calendar API test")
def test_reconcile_deletes_only_absent_future_managed_events_and_empty_feed_is_noop():
    config = load_config()
    test_calendar_id = os.getenv("ONCALL_SYNC_TEST_CALENDAR_ID")
    if not test_calendar_id or config.target_calendar_id != test_calendar_id:
        pytest.fail("target must match ONCALL_SYNC_TEST_CALENDAR_ID")
    gateway = GoogleCalendarGateway(build_calendar_service(load_credentials(config.oauth_token_file, ["https://www.googleapis.com/auth/calendar.events"])), config.target_calendar_id)
    marker = f"integration-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    start = now + timedelta(days=2)
    end = start + timedelta(hours=8)

    def managed_body(uid, summary, event_start, event_end):
        return {
            "summary": summary,
            "start": {"dateTime": event_start.isoformat()},
            "end": {"dateTime": event_end.isoformat()},
            "extendedProperties": {"private": {"oncallCalendarSync": marker, "sourceUid": uid}},
        }

    sentinel_id = None
    try:
        sentinel = gateway.create_event({
            "summary": f"Temporary unmarked sentinel {uuid.uuid4()}",
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": (start + timedelta(hours=1)).isoformat()},
        })
        sentinel_id = sentinel["id"]
        past_start = now - timedelta(days=3)
        gateway.create_event(managed_body("past", "Past managed history", past_start, past_start + timedelta(hours=8)))
        stale_start = now + timedelta(days=10)
        stale = gateway.create_event(managed_body("removed", "Removed shift", stale_start, stale_start + timedelta(hours=8)))
        current = gateway.create_event(managed_body("current", "Old shift title", start, end))

        desired = Shift("current", start, end, "Updated shift title")
        result = reconcile([desired], gateway, marker, now=now)

        assert not result.failed
        assert result.updated == 1
        assert result.removed == 1
        remaining = gateway.list_managed_events(marker)
        by_uid = {event["extendedProperties"]["private"]["sourceUid"]: event for event in remaining}
        assert by_uid["current"]["id"] == current["id"]
        assert by_uid["current"]["summary"] == "Updated shift title"
        assert "past" in by_uid
        assert "removed" not in by_uid
        assert all_events_contain(gateway, sentinel_id)

        before_empty_run = {event["id"] for event in remaining}
        empty_result = reconcile([], gateway, marker, now=now)
        assert empty_result.failed and empty_result.error_category == "source_empty"
        assert {event["id"] for event in gateway.list_managed_events(marker)} == before_empty_run
        assert all_events_contain(gateway, sentinel_id)
    finally:
        for event in gateway.list_managed_events(marker):
            gateway.delete_event(event["id"])
        if sentinel_id:
            gateway.delete_event(sentinel_id)


def all_events_contain(gateway, event_id):
    return any(event.get("id") == event_id for event in gateway.list_events())
