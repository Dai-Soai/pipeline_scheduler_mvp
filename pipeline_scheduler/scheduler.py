from datetime import datetime, timezone
from typing import Any

from pipeline_scheduler.contract import RetrySchedule, RetryTask
from pipeline_scheduler.delay import calculate_retry_run_at


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def calculate_run_at(
    generated_at: str,
    delay_seconds: int,
) -> str:
    return calculate_retry_run_at(generated_at, delay_seconds)


def build_candidate_index(retry_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        candidate["node_id"]: candidate
        for candidate in retry_plan.get("candidates", [])
        if isinstance(candidate, dict) and candidate.get("node_id")
    }


def build_retry_tasks(
    retry_plan: dict[str, Any],
    generated_at: str,
) -> list[RetryTask]:
    candidate_index = build_candidate_index(retry_plan)
    tasks: list[RetryTask] = []

    for decision in retry_plan.get("decisions", []):
        if not isinstance(decision, dict):
            raise ValueError("decision item must be an object")

        if decision.get("should_retry") is not True:
            continue

        node_id = decision.get("node_id")
        if not node_id:
            raise ValueError("retry decision requires node_id")

        next_attempt = decision.get("next_attempt")
        if next_attempt is None:
            raise ValueError("retry decision requires next_attempt")

        delay_seconds = decision.get("delay_seconds", 0)
        if delay_seconds is None:
            delay_seconds = 0

        candidate = candidate_index.get(node_id, {})
        node_name = candidate.get("node_name") or node_id

        tasks.append(
            RetryTask(
                node_id=str(node_id),
                node_name=str(node_name),
                run_at=calculate_run_at(generated_at, int(delay_seconds)),
                delay_seconds=int(delay_seconds),
                next_attempt=int(next_attempt),
                status="scheduled",
                reason=decision.get("reason"),
                metadata={
                    "decision": decision,
                    "candidate": candidate,
                },
            )
        )

    return tasks


def build_retry_schedule(
    retry_plan: dict[str, Any],
    generated_at: str | None = None,
) -> RetrySchedule:
    pipeline_id = retry_plan.get("pipeline_id")
    if not pipeline_id:
        raise ValueError("retry_plan requires pipeline_id")

    if generated_at is None:
        generated_at = utc_now_iso()

    tasks = build_retry_tasks(retry_plan, generated_at=generated_at)
    status = "ready" if tasks else "empty"

    return RetrySchedule(
        pipeline_id=str(pipeline_id),
        status=status,
        generated_at=generated_at,
        tasks=tasks,
        metadata={
            "source": "retry_plan",
            "total_tasks": len(tasks),
        },
    )
