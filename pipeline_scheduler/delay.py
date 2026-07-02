from datetime import datetime, timedelta, timezone


def parse_utc_timestamp(timestamp: str) -> datetime:
    if not timestamp:
        raise ValueError("timestamp is required")

    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def to_utc_iso(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def add_delay_seconds(
    timestamp: str,
    delay_seconds: int,
) -> str:
    if delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative")

    base_time = parse_utc_timestamp(timestamp)
    run_time = base_time + timedelta(seconds=delay_seconds)

    return to_utc_iso(run_time)


def normalize_delay_seconds(value: int | float | None) -> int:
    if value is None:
        return 0

    delay = int(value)

    if delay < 0:
        raise ValueError("delay_seconds cannot be negative")

    return delay


def calculate_retry_run_at(
    generated_at: str,
    delay_seconds: int | float | None,
) -> str:
    return add_delay_seconds(
        timestamp=generated_at,
        delay_seconds=normalize_delay_seconds(delay_seconds),
    )
