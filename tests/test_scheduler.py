import pytest

from pipeline_scheduler.contract import RetrySchedule, RetryTask
from pipeline_scheduler.scheduler import (
    build_candidate_index,
    build_retry_schedule,
    build_retry_tasks,
    calculate_run_at,
)


def sample_retry_plan():
    return {
        "pipeline_id": "pipeline-001",
        "candidates": [
            {
                "node_id": "execute",
                "node_name": "Execute Pipeline",
                "status": "failed",
                "metadata": {
                    "error": "Execution failed",
                },
            },
            {
                "node_id": "notify",
                "node_name": "Notify Result",
                "status": "blocked",
            },
        ],
        "decisions": [
            {
                "node_id": "execute",
                "decision": "retry",
                "should_retry": True,
                "next_attempt": 2,
                "delay_seconds": 20,
                "reason": "retry allowed",
            },
            {
                "node_id": "notify",
                "decision": "skip",
                "should_retry": False,
                "next_attempt": None,
                "delay_seconds": None,
                "reason": "not retryable",
            },
        ],
    }


def test_calculate_run_at():
    run_at = calculate_run_at(
        generated_at="2026-07-02T20:40:00Z",
        delay_seconds=20,
    )

    assert run_at == "2026-07-02T20:40:20Z"


def test_build_candidate_index():
    index = build_candidate_index(sample_retry_plan())

    assert "execute" in index
    assert index["execute"]["node_name"] == "Execute Pipeline"


def test_build_retry_tasks_from_retry_decisions():
    tasks = build_retry_tasks(
        sample_retry_plan(),
        generated_at="2026-07-02T20:40:00Z",
    )

    assert len(tasks) == 1
    assert isinstance(tasks[0], RetryTask)
    assert tasks[0].node_id == "execute"
    assert tasks[0].node_name == "Execute Pipeline"
    assert tasks[0].run_at == "2026-07-02T20:40:20Z"
    assert tasks[0].next_attempt == 2
    assert tasks[0].delay_seconds == 20


def test_build_retry_tasks_preserves_metadata():
    tasks = build_retry_tasks(
        sample_retry_plan(),
        generated_at="2026-07-02T20:40:00Z",
    )

    assert tasks[0].metadata["candidate"]["metadata"]["error"] == "Execution failed"
    assert tasks[0].metadata["decision"]["decision"] == "retry"


def test_build_retry_tasks_uses_node_id_as_name_when_candidate_missing():
    retry_plan = {
        "pipeline_id": "pipeline-001",
        "candidates": [],
        "decisions": [
            {
                "node_id": "missing-node",
                "decision": "retry",
                "should_retry": True,
                "next_attempt": 1,
                "delay_seconds": 5,
            }
        ],
    }

    tasks = build_retry_tasks(
        retry_plan,
        generated_at="2026-07-02T20:40:00Z",
    )

    assert tasks[0].node_name == "missing-node"


def test_build_retry_tasks_rejects_non_object_decision():
    with pytest.raises(ValueError):
        build_retry_tasks(
            {
                "pipeline_id": "pipeline-001",
                "decisions": ["bad-decision"],
            },
            generated_at="2026-07-02T20:40:00Z",
        )


def test_build_retry_tasks_requires_node_id():
    with pytest.raises(ValueError):
        build_retry_tasks(
            {
                "pipeline_id": "pipeline-001",
                "decisions": [
                    {
                        "decision": "retry",
                        "should_retry": True,
                        "next_attempt": 1,
                        "delay_seconds": 5,
                    }
                ],
            },
            generated_at="2026-07-02T20:40:00Z",
        )


def test_build_retry_tasks_requires_next_attempt():
    with pytest.raises(ValueError):
        build_retry_tasks(
            {
                "pipeline_id": "pipeline-001",
                "decisions": [
                    {
                        "node_id": "execute",
                        "decision": "retry",
                        "should_retry": True,
                        "delay_seconds": 5,
                    }
                ],
            },
            generated_at="2026-07-02T20:40:00Z",
        )


def test_build_retry_schedule_ready():
    schedule = build_retry_schedule(
        sample_retry_plan(),
        generated_at="2026-07-02T20:40:00Z",
    )

    assert isinstance(schedule, RetrySchedule)
    assert schedule.pipeline_id == "pipeline-001"
    assert schedule.status == "ready"
    assert len(schedule.tasks) == 1
    assert schedule.metadata["total_tasks"] == 1


def test_build_retry_schedule_empty():
    schedule = build_retry_schedule(
        {
            "pipeline_id": "pipeline-001",
            "candidates": [],
            "decisions": [],
        },
        generated_at="2026-07-02T20:40:00Z",
    )

    assert schedule.status == "empty"
    assert schedule.tasks == []


def test_build_retry_schedule_requires_pipeline_id():
    with pytest.raises(ValueError):
        build_retry_schedule(
            {
                "decisions": [],
            },
            generated_at="2026-07-02T20:40:00Z",
        )
