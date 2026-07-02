import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pipeline_scheduler.contract import RetrySchedule
from pipeline_scheduler.loader import load_retry_plan
from pipeline_scheduler.queue import get_queue_summary
from pipeline_scheduler.scheduler import build_retry_schedule


def schedule_to_dict(schedule: RetrySchedule) -> dict[str, Any]:
    return {
        "pipeline_id": schedule.pipeline_id,
        "status": schedule.status,
        "generated_at": schedule.generated_at,
        "tasks": [asdict(task) for task in schedule.tasks],
        "summary": get_queue_summary(schedule),
        "metadata": schedule.metadata,
    }


def write_schedule_json(
    schedule: RetrySchedule,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = schedule_to_dict(schedule)

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return path


def build_schedule_from_file(
    retry_plan_path: str | Path,
    generated_at: str | None = None,
) -> RetrySchedule:
    retry_plan = load_retry_plan(retry_plan_path)
    return build_retry_schedule(retry_plan, generated_at=generated_at)
