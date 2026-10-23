import os

import pytest

from opsgenie_google_calendar_sync.config import ConfigError, load_config


def test_loads_required_settings_and_default_oauth_names(tmp_path):
    (tmp_path / "config.toml").write_text(
        'source_ical_url="https://example.invalid/feed"\ntarget_calendar_id="cal"\n'
    )
    config = load_config(config_dir=tmp_path)
    assert config.source_ical_url == "https://example.invalid/feed"
    assert config.target_calendar_id == "cal"
    assert config.oauth_client_file == tmp_path / "oauth-client.json"
    assert config.oauth_token_file == tmp_path / "token.json"


@pytest.mark.parametrize("contents", ["", "[", "[]", 'source_ical_url="x"'])
def test_rejects_missing_required_keys(tmp_path, contents):
    (tmp_path / "config.toml").write_text(contents)
    with pytest.raises(ConfigError):
        load_config(config_dir=tmp_path)


def test_missing_file_has_sanitized_error(tmp_path):
    with pytest.raises(ConfigError) as exc:
        load_config(config_dir=tmp_path)
    assert str(tmp_path) not in str(exc.value)


@pytest.mark.parametrize("key,value", [("source_ical_url", "not-a-url"), ("target_calendar_id", "")])
def test_rejects_invalid_values(tmp_path, key, value):
    settings = {"source_ical_url": '"https://example.invalid/feed"', "target_calendar_id": '"cal"'}
    settings[key] = repr(value)
    (tmp_path / "config.toml").write_text("\n".join(f"{k}={v}" for k, v in settings.items()))
    with pytest.raises(ConfigError):
        load_config(config_dir=tmp_path)


def test_environment_overrides_config_dir(tmp_path, monkeypatch):
    (tmp_path / "config.toml").write_text(
        'source_ical_url="https://example.invalid/feed"\ntarget_calendar_id="cal"\n'
    )
    monkeypatch.setenv("OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR", str(tmp_path))
    assert load_config().target_calendar_id == "cal"
