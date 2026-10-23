"""Google OAuth credential loading and Calendar API gateway."""

from pathlib import Path

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarAccessError(Exception):
    """Calendar operation failed; message is safe for routine output."""


def load_credentials(token_file: Path, scopes: list[str]) -> Credentials:
    try:
        credentials = Credentials.from_authorized_user_file(str(token_file), scopes)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials.valid:
            raise CalendarAccessError("authorization_required")
        return credentials
    except (OSError, ValueError, GoogleAuthError, HttpError) as exc:
        raise CalendarAccessError("authorization_failed") from exc


def build_calendar_service(credentials):
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


class GoogleCalendarGateway:
    def __init__(self, service, calendar_id: str):
        self.service = service
        self.calendar_id = calendar_id

    def _call(self, request):
        try:
            return request.execute()
        except HttpError as exc:
            code = getattr(exc.resp, "status", "unknown")
            raise CalendarAccessError(f"calendar_api_error_{code}") from exc
        except Exception as exc:
            raise CalendarAccessError("calendar_api_error") from exc

    def list_events(self, **kwargs):
        events, token = [], None
        while True:
            params = {**kwargs, "calendarId": self.calendar_id, "maxResults": 2500}
            if token:
                params["pageToken"] = token
            page = self._call(self.service.events().list(**params))
            events.extend(page.get("items", []))
            token = page.get("nextPageToken")
            if not token:
                return events

    def list_managed_events(self, marker: str):
        return self.list_events(privateExtendedProperty=f"oncallCalendarSync={marker}")

    def create_event(self, body):
        return self._call(self.service.events().insert(calendarId=self.calendar_id, body=body))

    def update_event(self, event_id, body):
        return self._call(self.service.events().update(calendarId=self.calendar_id, eventId=event_id, body=body))

    def delete_event(self, event_id):
        return self._call(self.service.events().delete(calendarId=self.calendar_id, eventId=event_id))
