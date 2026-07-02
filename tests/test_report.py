import json

from pipeline_scheduler.contract import RetrySchedule
from pipeline_scheduler.report import (
    build_schedule_from_file,
    schedule_to_dict,
    write_schedule_json,
)
from pipeline_scheduler.scheduler import build_retry_schedule


def sample_retry_plan():
    return {
        "pipeline_id": "pipeline-001",
        "policy": {},
        "candidates": [
            {
                "node_id": "execute",
                "node_name": "Execute Pipeline",
                "status": "failed",
            }
        ],
        "decisions": [
            {
                "node_id": "execute",
                "decision": "retry",
                "should_retry": True,
                "next_attempt": 2,
                "delay_seconds": 20,
                "reason": "retry allowed",
            }
        ],
        "summary": {},
    }


def test_schedule_to_dict():
    schedule = build_retry_schedule(
        sample_retry_plan(),
        generated_at="2026-07-02T20:40:00Z",
    )

    payload = schedule_to_dict(schedule)

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "ready"
    assert payload["tasks"][0]["node_id"] == "execute"
    assert payload["summary"]["queued_tasks"] == 1


def test_write_schedule_json(tmp_path):
    schedule = build_retry_schedule(
        sample_retry_plan(),
        generated_at="2026-07-02T20:40:00Z",
    )
    output_file = tmp_path / "schedule.json"

    written_path = write_schedule_json(schedule, output_file)

    assert written_path == output_file
    assert output_file.exists()

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["tasks"][0]["run_at"] == "2026-07-02T20:40:20Z"


def test_build_schedule_from_file(tmp_path):
    retry_plan_file = tmp_path / "retry_plan.json"
    retry_plan_file.write_text(
        json.dumps(sample_retry_plan()),
        encoding="utf-8",
    )

    schedule = build_schedule_from_file(
        retry_plan_file,
        generated_at="2026-07-02T20:40:00Z",
    )

    assert isinstance(schedule, RetrySchedule)
    assert schedule.pipeline_id == "pipeline-001"
    assert len(schedule.tasks) == 1
