import pytest
from datetime import datetime, timezone

from pipeline_scheduler.delay import (
    add_delay_seconds,
    calculate_retry_run_at,
    normalize_delay_seconds,
    parse_utc_timestamp,
    to_utc_iso,
)


def test_parse_utc_timestamp():
    value = parse_utc_timestamp("2026-07-02T20:40:00Z")

    assert value.year == 2026
    assert value.tzinfo is not None


def test_parse_utc_timestamp_rejects_empty_timestamp():
    with pytest.raises(ValueError):
        parse_utc_timestamp("")


def test_to_utc_iso():
    value = datetime(2026, 7, 2, 20, 40, 0, tzinfo=timezone.utc)

    assert to_utc_iso(value) == "2026-07-02T20:40:00Z"


def test_add_delay_seconds():
    run_at = add_delay_seconds(
        timestamp="2026-07-02T20:40:00Z",
        delay_seconds=30,
    )

    assert run_at == "2026-07-02T20:40:30Z"


def test_add_delay_seconds_rejects_negative_delay():
    with pytest.raises(ValueError):
        add_delay_seconds(
            timestamp="2026-07-02T20:40:00Z",
            delay_seconds=-1,
        )


def test_normalize_delay_seconds_none_to_zero():
    assert normalize_delay_seconds(None) == 0


def test_normalize_delay_seconds_float_to_int():
    assert normalize_delay_seconds(10.9) == 10


def test_normalize_delay_seconds_rejects_negative():
    with pytest.raises(ValueError):
        normalize_delay_seconds(-5)


def test_calculate_retry_run_at():
    run_at = calculate_retry_run_at(
        generated_at="2026-07-02T20:40:00Z",
        delay_seconds=20,
    )

    assert run_at == "2026-07-02T20:40:20Z"
