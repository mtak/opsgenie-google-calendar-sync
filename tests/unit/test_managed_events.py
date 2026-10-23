from datetime import datetime, timezone

from opsgenie_google_calendar_sync.opsgenie_ical import Shift
from opsgenie_google_calendar_sync.reconcile import reconcile


def test_updates_only_marker_owned_events_and_never_deletes_unrelated():
    shift = Shift("uid-1", datetime(2030, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, 1, tzinfo=timezone.utc), "source")
    managed = {"id": "managed", "summary": "edited", "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "uid-1"}}, "start": {"dateTime": "2030-01-01T00:00:00+00:00"}, "end": {"dateTime": "2030-01-01T01:00:00+00:00"}}
    unrelated = {"id": "family", "summary": "birthday", "extendedProperties": {"private": {}}}

    class Gateway:
        writes = []
        def list_managed_events(self, marker): return [managed, unrelated]
        def update_event(self, event_id, body): self.writes.append(("update", event_id))
        def delete_event(self, event_id): self.writes.append(("delete", event_id))
        def create_event(self, body): self.writes.append(("create", body))

    gateway = Gateway()
    result = reconcile([shift], gateway, "marker")
    assert result.updated == 1
    assert gateway.writes == [("update", "managed")]


def test_empty_feed_does_not_read_or_delete_any_calendar_events():
    class Gateway:
        def list_managed_events(self, marker): raise AssertionError("empty feed must stop before calendar access")
        def delete_event(self, event_id): raise AssertionError("empty feed must not delete")
    result = reconcile([], Gateway(), "marker")
    assert result.failed
    assert result.error_category == "source_empty"


def test_deletes_absent_future_managed_event_and_preserves_past_and_unmarked_events():
    shift = Shift("current", datetime(2030, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, 1, tzinfo=timezone.utc), "current")
    future = {"id": "stale", "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "removed"}}, "end": {"dateTime": "2030-02-01T01:00:00Z"}}
    past = {"id": "past", "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "past"}}, "end": {"dateTime": "2020-01-01T01:00:00Z"}}
    unrelated = {"id": "family", "extendedProperties": {"private": {}}, "end": {"dateTime": "2030-02-01T01:00:00Z"}}

    class Gateway:
        writes = []
        def list_managed_events(self, marker): return [future, past, unrelated]
        def create_event(self, body): self.writes.append(("create", body))
        def update_event(self, event_id, body): self.writes.append(("update", event_id))
        def delete_event(self, event_id): self.writes.append(("delete", event_id))

    gateway = Gateway()
    result = reconcile([shift], gateway, "marker", now=datetime(2029, 1, 1, tzinfo=timezone.utc))
    assert result.removed == 1
    assert gateway.writes == [("create", gateway.writes[0][1]), ("delete", "stale")]
    assert gateway.writes[0][1]["extendedProperties"]["private"]["sourceUid"] == "current"


def test_uid_rotation_rebinds_unchanged_event_without_recreating_it():
    shift = Shift("new-uid", datetime(2030, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, 1, tzinfo=timezone.utc), "same shift")
    old = {"id": "g1", "summary": "same shift", "description": "", "location": "", "start": {"dateTime": "2030-01-01T00:00:00+00:00"}, "end": {"dateTime": "2030-01-01T01:00:00+00:00"}, "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "old-uid"}}}

    class Gateway:
        writes = []
        def list_managed_events(self, marker): return [old]
        def create_event(self, body): self.writes.append(("create", body))
        def update_event(self, event_id, body): self.writes.append(("update", event_id, body))
        def delete_event(self, event_id): self.writes.append(("delete", event_id))

    gateway = Gateway()
    result = reconcile([shift], gateway, "marker", now=datetime(2029, 1, 1, tzinfo=timezone.utc))
    assert result.updated == 1
    assert result.added == result.removed == 0
    assert len(gateway.writes) == 1 and gateway.writes[0][0] == "update"
    assert gateway.writes[0][2]["extendedProperties"]["private"]["sourceUid"] == "new-uid"


def test_past_managed_event_is_not_rewritten():
    past_shift = Shift("old", datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2020, 1, 1, 1, tzinfo=timezone.utc), "changed source")
    old_event = {"id": "past", "summary": "original history", "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "old"}}, "start": {"dateTime": "2020-01-01T00:00:00Z"}, "end": {"dateTime": "2020-01-01T01:00:00Z"}}

    class Gateway:
        writes = []
        def list_managed_events(self, marker): return [old_event]
        def update_event(self, *args): self.writes.append(args)
        def delete_event(self, *args): self.writes.append(args)
        def create_event(self, *args): self.writes.append(args)

    gateway = Gateway()
    assert reconcile([past_shift], gateway, "marker").updated == 0
    assert gateway.writes == []


def test_duplicate_managed_source_uids_fail_before_any_write():
    shift = Shift("duplicate", datetime(2030, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, 1, tzinfo=timezone.utc), "shift")
    first = {"id": "one", "end": {"dateTime": "2030-01-01T01:00:00Z"}, "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "duplicate"}}}
    second = {"id": "two", "end": {"dateTime": "2030-01-02T01:00:00Z"}, "extendedProperties": {"private": {"oncallCalendarSync": "marker", "sourceUid": "duplicate"}}}

    class Gateway:
        writes = []
        def list_managed_events(self, marker): return [first, second]
        def create_event(self, body): self.writes.append(("create", body))
        def update_event(self, event_id, body): self.writes.append(("update", event_id))
        def delete_event(self, event_id): self.writes.append(("delete", event_id))

    gateway = Gateway()
    result = reconcile([shift], gateway, "marker")
    assert result.failed
    assert result.error_category == "managed_identity_ambiguous"
    assert gateway.writes == []
