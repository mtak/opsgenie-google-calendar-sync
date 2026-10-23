"""Command line entry point for authorization and one-shot synchronization."""

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from .config import ConfigError, load_config
from .google_calendar import GoogleCalendarGateway, build_calendar_service, load_credentials
from .opsgenie_ical import FeedError, fetch_feed, parse_feed
from .reconcile import SYNC_MARKER, reconcile

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


@dataclass(frozen=True)
class SyncOutcome:
    outcome: str
    added: int = 0
    updated: int = 0
    removed: int = 0
    error_category: str = ""


def authorize(config, flow_class=InstalledAppFlow):
    try:
        flow = flow_class.from_client_secrets_file(str(config.oauth_client_file), SCOPES)
        credentials = flow.run_local_server(port=0, open_browser=True)
        config.oauth_token_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(config.oauth_token_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as token_file:
            os.fchmod(descriptor, 0o600)
            token_file.write(credentials.to_json())
    except Exception as exc:
        raise RuntimeError("authorization_failed") from exc


def sync_once(config) -> SyncOutcome:
    try:
        shifts = parse_feed(fetch_feed(config.source_ical_url))
    except FeedError as exc:
        return SyncOutcome("failure", error_category=str(exc))
    try:
        credentials = load_credentials(config.oauth_token_file, SCOPES)
        gateway = GoogleCalendarGateway(build_calendar_service(credentials), config.target_calendar_id)
    except Exception:
        return SyncOutcome("failure", error_category="authorization")
    result = reconcile(shifts, gateway, SYNC_MARKER)
    return SyncOutcome("failure" if result.failed else "success", result.added, result.updated, result.removed, result.error_category)


def _report(result: SyncOutcome):
    if result.outcome == "success":
        print(f"status=success added={result.added} updated={result.updated} removed={result.removed}")
        return 0
    print(f"status=failure category={result.error_category or 'sync_failed'} added={result.added} updated={result.updated} removed={result.removed}", file=sys.stderr)
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="oncall-calendar-sync")
    parser.add_argument("command", choices=("authorize", "sync"))
    parser.add_argument("--config-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config_dir)
    except ConfigError as exc:
        print(f"status=failure category=configuration ({exc})", file=sys.stderr)
        return 1
    if args.command == "authorize":
        try:
            authorize(config)
        except RuntimeError:
            print("status=failure category=authorization", file=sys.stderr)
            return 1
        print("status=success authorization_saved")
        return 0
    return _report(sync_once(config))


if __name__ == "__main__":
    raise SystemExit(main())
