from unittest.mock import Mock
from datetime import datetime, timedelta, timezone

import pytest
from googleapiclient.errors import HttpError

from oncall_calendar_sync.google_calendar import CalendarAccessError, GoogleCalendarGateway, load_credentials


def test_refresh_token_credentials_loaded_from_private_file(tmp_path):
    token = tmp_path / "token.json"
    expiry = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    token.write_text('{"token": "access", "refresh_token": "refresh", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "id", "client_secret": "secret", "scopes": ["scope"], "expiry": "' + expiry + '"}')
    credentials = load_credentials(token, ["scope"])
    assert credentials.refresh_token == "refresh"


def test_expired_credentials_refresh_in_memory_without_persisting_access_token(tmp_path, monkeypatch):
    token = tmp_path / "token.json"
    token.write_text("original")
    credentials = Mock(expired=True, refresh_token="refresh", valid=True)
    monkeypatch.setattr("oncall_calendar_sync.google_calendar.Credentials.from_authorized_user_file", lambda *args: credentials)
    assert load_credentials(token, ["scope"]) is credentials
    credentials.refresh.assert_called_once()
    assert token.read_text() == "original"


def test_list_events_paginates():
    service = Mock()
    service.events.return_value.list.return_value.execute.side_effect = [
        {"items": [{"id": "one"}], "nextPageToken": "next"},
        {"items": [{"id": "two"}]},
    ]
    gateway = GoogleCalendarGateway(service, "calendar")
    assert [event["id"] for event in gateway.list_events()] == ["one", "two"]
    assert service.events.return_value.list.call_count == 2


def test_managed_event_query_uses_private_application_marker():
    service = Mock()
    service.events.return_value.list.return_value.execute.return_value = {"items": []}
    gateway = GoogleCalendarGateway(service, "calendar-id")
    assert gateway.list_managed_events("application-marker") == []
    service.events.return_value.list.assert_called_once_with(
        calendarId="calendar-id",
        maxResults=2500,
        privateExtendedProperty="oncallCalendarSync=application-marker",
    )


def test_later_page_read_error_is_sanitized():
    service = Mock()
    first_page = Mock()
    first_page.execute.return_value = {"items": [{"id": "managed"}], "nextPageToken": "next"}
    second_page = Mock()
    second_page.execute.side_effect = RuntimeError("private response body")
    service.events.return_value.list.side_effect = [first_page, second_page]
    gateway = GoogleCalendarGateway(service, "calendar")
    with pytest.raises(CalendarAccessError, match="calendar_api_error") as exc:
        gateway.list_managed_events("marker")
    assert "private response body" not in str(exc.value)
    assert service.events.return_value.list.call_count == 2


@pytest.mark.parametrize("method,operation", [("create_event", "insert"), ("update_event", "update"), ("delete_event", "delete")])
def test_mutations_call_calendar_api(method, operation):
    service = Mock()
    gateway = GoogleCalendarGateway(service, "calendar")
    args = ("event-id", {"summary": "x"}) if method == "update_event" else (("event-id",) if method == "delete_event" else ({"summary": "x"},))
    getattr(gateway, method)(*args)
    getattr(service.events.return_value, operation).assert_called_once()


def test_permission_errors_propagate_without_response_body():
    service = Mock()
    service.events.return_value.list.return_value.execute.side_effect = RuntimeError("403 permission denied private-body")
    with pytest.raises(Exception) as exc:
        GoogleCalendarGateway(service, "calendar").list_events()
    assert "private-body" not in str(exc.value)


def test_http_403_is_sanitized_and_identifiable():
    service = Mock()
    response = Mock(status=403)
    service.events.return_value.list.return_value.execute.side_effect = HttpError(response, b"private response body")
    with pytest.raises(Exception, match="calendar_api_error_403") as exc:
        GoogleCalendarGateway(service, "calendar").list_events()
    assert "private response body" not in str(exc.value)
