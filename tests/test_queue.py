from pipeline_scheduler.contract import RetrySchedule, RetryTask
from pipeline_scheduler.queue import (
    build_execution_queue,
    count_pending_tasks,
    filter_scheduled_tasks,
    get_queue_summary,
    sort_retry_tasks,
)


def make_task(
    node_id: str,
    run_at: str,
    status: str = "scheduled",
) -> RetryTask:
    return RetryTask(
        node_id=node_id,
        node_name=node_id,
        run_at=run_at,
        delay_seconds=0,
        next_attempt=1,
        status=status,
    )


def make_schedule(tasks: list[RetryTask]) -> RetrySchedule:
    return RetrySchedule(
        pipeline_id="pipeline-001",
        status="ready" if tasks else "empty",
        generated_at="2026-07-02T20:40:00Z",
        tasks=tasks,
    )


def test_sort_retry_tasks_by_run_at():
    late = make_task("late", "2026-07-02T20:40:30Z")
    early = make_task("early", "2026-07-02T20:40:05Z")
    middle = make_task("middle", "2026-07-02T20:40:10Z")

    sorted_tasks = sort_retry_tasks([late, early, middle])

    assert [task.node_id for task in sorted_tasks] == [
        "early",
        "middle",
        "late",
    ]


def test_sort_retry_tasks_returns_new_sorted_list():
    late = make_task("late", "2026-07-02T20:40:30Z")
    early = make_task("early", "2026-07-02T20:40:05Z")
    tasks = [late, early]

    sorted_tasks = sort_retry_tasks(tasks)

    assert sorted_tasks[0].node_id == "early"
    assert tasks[0].node_id == "late"


def test_filter_scheduled_tasks():
    tasks = [
        make_task("a", "2026-07-02T20:40:05Z", status="scheduled"),
        make_task("b", "2026-07-02T20:40:10Z", status="cancelled"),
        make_task("c", "2026-07-02T20:40:15Z", status="scheduled"),
    ]

    filtered = filter_scheduled_tasks(tasks)

    assert len(filtered) == 2
    assert [task.node_id for task in filtered] == ["a", "c"]


def test_build_execution_queue_filters_and_sorts_tasks():
    tasks = [
        make_task("late", "2026-07-02T20:40:30Z"),
        make_task("cancelled", "2026-07-02T20:40:01Z", status="cancelled"),
        make_task("early", "2026-07-02T20:40:05Z"),
        make_task("middle", "2026-07-02T20:40:10Z"),
    ]
    schedule = make_schedule(tasks)

    queue = build_execution_queue(schedule)

    assert [task.node_id for task in queue] == [
        "early",
        "middle",
        "late",
    ]


def test_count_pending_tasks():
    schedule = make_schedule(
        [
            make_task("a", "2026-07-02T20:40:05Z"),
            make_task("b", "2026-07-02T20:40:10Z"),
            make_task("c", "2026-07-02T20:40:15Z", status="cancelled"),
        ]
    )

    assert count_pending_tasks(schedule) == 2


def test_get_queue_summary():
    schedule = make_schedule(
        [
            make_task("late", "2026-07-02T20:40:30Z"),
            make_task("early", "2026-07-02T20:40:05Z"),
        ]
    )

    summary = get_queue_summary(schedule)

    assert summary["pipeline_id"] == "pipeline-001"
    assert summary["total_tasks"] == 2
    assert summary["queued_tasks"] == 2
    assert summary["first_run_at"] == "2026-07-02T20:40:05Z"
    assert summary["last_run_at"] == "2026-07-02T20:40:30Z"


def test_get_queue_summary_empty_queue():
    schedule = make_schedule([])

    summary = get_queue_summary(schedule)

    assert summary["total_tasks"] == 0
    assert summary["queued_tasks"] == 0
    assert summary["first_run_at"] is None
    assert summary["last_run_at"] is None
