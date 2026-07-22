from typing import Any
from pipeline_scheduler.contract import RetrySchedule, RetryTask


def sort_retry_tasks(tasks: list[RetryTask]) -> list[RetryTask]:
    return sorted(tasks, key=lambda task: task.run_at)


def filter_scheduled_tasks(tasks: list[RetryTask]) -> list[RetryTask]:
    return [task for task in tasks if task.status == "scheduled"]


def build_execution_queue(schedule: RetrySchedule) -> list[RetryTask]:
    scheduled_tasks = filter_scheduled_tasks(schedule.tasks)
    return sort_retry_tasks(scheduled_tasks)


def count_pending_tasks(schedule: RetrySchedule) -> int:
    return len(filter_scheduled_tasks(schedule.tasks))


def get_queue_summary(schedule: RetrySchedule) -> dict[str, Any]:
    queue = build_execution_queue(schedule)

    return {
        "pipeline_id": schedule.pipeline_id,
        "total_tasks": len(schedule.tasks),
        "queued_tasks": len(queue),
        "first_run_at": queue[0].run_at if queue else None,
        "last_run_at": queue[-1].run_at if queue else None,
    }
