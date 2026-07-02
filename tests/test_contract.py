import pytest

from pipeline_scheduler.contract import RetrySchedule, RetryTask


def test_retry_task_creation():
    task = RetryTask(
        node_id="execute",
        node_name="Execute Pipeline",
        run_at="2026-07-02T20:45:00Z",
        delay_seconds=20,
        next_attempt=2,
        reason="retry allowed",
    )

    assert task.node_id == "execute"
    assert task.status == "scheduled"
    assert task.delay_seconds == 20
    assert task.next_attempt == 2


def test_retry_task_rejects_missing_node_id():
    with pytest.raises(ValueError):
        RetryTask(
            node_id="",
            node_name="Execute Pipeline",
            run_at="2026-07-02T20:45:00Z",
            delay_seconds=20,
            next_attempt=2,
        )


def test_retry_task_rejects_negative_delay():
    with pytest.raises(ValueError):
        RetryTask(
            node_id="execute",
            node_name="Execute Pipeline",
            run_at="2026-07-02T20:45:00Z",
            delay_seconds=-1,
            next_attempt=2,
        )


def test_retry_task_rejects_invalid_next_attempt():
    with pytest.raises(ValueError):
        RetryTask(
            node_id="execute",
            node_name="Execute Pipeline",
            run_at="2026-07-02T20:45:00Z",
            delay_seconds=20,
            next_attempt=0,
        )


def test_retry_task_rejects_invalid_status():
    with pytest.raises(ValueError):
        RetryTask(
            node_id="execute",
            node_name="Execute Pipeline",
            run_at="2026-07-02T20:45:00Z",
            delay_seconds=20,
            next_attempt=2,
            status="bad",
        )


def test_retry_schedule_creation():
    task = RetryTask(
        node_id="execute",
        node_name="Execute Pipeline",
        run_at="2026-07-02T20:45:00Z",
        delay_seconds=20,
        next_attempt=2,
    )

    schedule = RetrySchedule(
        pipeline_id="pipeline-001",
        status="ready",
        generated_at="2026-07-02T20:40:00Z",
        tasks=[task],
    )

    assert schedule.pipeline_id == "pipeline-001"
    assert schedule.status == "ready"
    assert len(schedule.tasks) == 1


def test_retry_schedule_rejects_missing_pipeline_id():
    with pytest.raises(ValueError):
        RetrySchedule(
            pipeline_id="",
            status="ready",
            generated_at="2026-07-02T20:40:00Z",
            tasks=[],
        )


def test_retry_schedule_rejects_invalid_status():
    with pytest.raises(ValueError):
        RetrySchedule(
            pipeline_id="pipeline-001",
            status="bad",
            generated_at="2026-07-02T20:40:00Z",
            tasks=[],
        )


def test_retry_schedule_rejects_invalid_task_type():
    with pytest.raises(TypeError):
        RetrySchedule(
            pipeline_id="pipeline-001",
            status="ready",
            generated_at="2026-07-02T20:40:00Z",
            tasks=["bad-task"],
        )
