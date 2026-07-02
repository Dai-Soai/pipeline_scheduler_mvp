from dataclasses import dataclass, field
from typing import Any


VALID_TASK_STATUSES = {
    "scheduled",
    "pending",
    "cancelled",
    "skipped",
}

VALID_SCHEDULE_STATUSES = {
    "ready",
    "empty",
    "invalid",
}


@dataclass(frozen=True)
class RetryTask:
    node_id: str
    node_name: str
    run_at: str
    delay_seconds: int
    next_attempt: int
    status: str = "scheduled"
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")

        if not self.node_name:
            raise ValueError("node_name is required")

        if not self.run_at:
            raise ValueError("run_at is required")

        if self.delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative")

        if self.next_attempt < 1:
            raise ValueError("next_attempt must be >= 1")

        if self.status not in VALID_TASK_STATUSES:
            raise ValueError(f"invalid task status: {self.status}")


@dataclass(frozen=True)
class RetrySchedule:
    pipeline_id: str
    status: str
    generated_at: str
    tasks: list[RetryTask]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pipeline_id:
            raise ValueError("pipeline_id is required")

        if not self.generated_at:
            raise ValueError("generated_at is required")

        if self.status not in VALID_SCHEDULE_STATUSES:
            raise ValueError(f"invalid schedule status: {self.status}")

        for task in self.tasks:
            if not isinstance(task, RetryTask):
                raise TypeError("tasks must contain RetryTask items")
