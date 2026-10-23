from datetime import datetime, timezone

import pytest


@pytest.fixture
def utc():
    return timezone.utc


@pytest.fixture
def sample_event():
    return {
        "uid": "shift-1",
        "summary": "On call",
        "start": datetime(2030, 1, 1, 9, tzinfo=timezone.utc),
        "end": datetime(2030, 1, 1, 17, tzinfo=timezone.utc),
    }
