from unittest.mock import Mock

from opsgenie_google_calendar_sync.google_calendar import GoogleCalendarGateway
from opsgenie_google_calendar_sync.reconcile import reconcile


class FakeGateway:
    def __init__(self, events=()):
        self.events = {event["extendedProperties"]["private"]["sourceUid"]: event for event in events}
        self.writes = []

    def list_managed_events(self, marker):
        return list(self.events.values())

    def create_event(self, body):
        self.writes.append(("create", body))

    def update_event(self, event_id, body):
        self.writes.append(("update", body))

    def delete_event(self, event_id):
        self.writes.append(("delete", event_id))


def test_adds_missing_updates_changed_and_idempotent(sample_event):
    gateway = FakeGateway()
    result = reconcile([sample_event], gateway, "marker")
    assert result.added == 1 and len(gateway.writes) == 1
    managed = gateway.writes[-1][1]
    gateway.events["shift-1"] = {**managed, "id": "g1"}
    gateway.writes.clear()
    assert reconcile([sample_event], gateway, "marker").updated == 0
    assert gateway.writes == []
    changed = {**sample_event, "summary": "Changed"}
    assert reconcile([changed], gateway, "marker").updated == 1


def test_rejects_ambiguous_source_before_any_writes(sample_event):
    gateway = FakeGateway()
    assert reconcile([sample_event, sample_event], gateway, "marker").failed
    assert gateway.writes == []


def test_utc_z_and_offset_spellings_are_idempotent(sample_event):
    gateway = FakeGateway()
    reconcile([sample_event], gateway, "marker")
    previous = gateway.writes[-1][1]
    previous["id"] = "g1"
    previous["start"]["dateTime"] = previous["start"]["dateTime"].replace("+00:00", "Z")
    gateway.events["shift-1"] = previous
    gateway.writes.clear()
    assert reconcile([sample_event], gateway, "marker").updated == 0
    assert gateway.writes == []


def test_later_page_calendar_read_failure_causes_zero_mutations(sample_event):
    service = Mock()
    first_page = Mock()
    first_page.execute.return_value = {"items": [], "nextPageToken": "next"}
    second_page = Mock()
    second_page.execute.side_effect = RuntimeError("private response body")
    service.events.return_value.list.side_effect = [first_page, second_page]
    gateway = GoogleCalendarGateway(service, "calendar")

    result = reconcile([sample_event], gateway, "marker")

    assert result.failed
    assert result.error_category == "calendar_read"
    service.events.return_value.insert.assert_not_called()
    service.events.return_value.update.assert_not_called()
    service.events.return_value.delete.assert_not_called()
