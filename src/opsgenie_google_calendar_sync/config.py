"""Private runtime configuration loading and validation."""

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib
from urllib.parse import urlparse


class ConfigError(Exception):
    """Configuration could not be loaded or validated."""


@dataclass(frozen=True)
class Config:
    source_ical_url: str
    target_calendar_id: str
    oauth_client_file: Path
    oauth_token_file: Path


def default_config_dir() -> Path:
    override = os.environ.get("OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR")
    return Path(override).expanduser() if override else Path.home() / ".config/opsgenie-google-calendar-sync"


def load_config(config_dir: Path | str | None = None) -> Config:
    directory = Path(config_dir).expanduser() if config_dir is not None else default_config_dir()
    try:
        raw = tomllib.loads((directory / "config.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeError) as exc:
        raise ConfigError("Configuration file is missing or invalid") from exc

    url = raw.get("source_ical_url")
    calendar = raw.get("target_calendar_id")
    if not isinstance(url, str) or urlparse(url).scheme not in {"https", "http"} or not urlparse(url).netloc:
        raise ConfigError("source_ical_url must be an HTTP(S) URL")
    if not isinstance(calendar, str) or not calendar.strip():
        raise ConfigError("target_calendar_id must be a non-empty string")

    def path_value(key: str, default: str) -> Path:
        value = raw.get(key, default)
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"{key} must be a non-empty path")
        path = Path(value).expanduser()
        return path if path.is_absolute() else directory / path

    return Config(url, calendar, path_value("oauth_client_file", "oauth-client.json"), path_value("oauth_token_file", "token.json"))
