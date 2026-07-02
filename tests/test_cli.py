import json

from pipeline_scheduler.cli import main


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


def test_cli_prints_help_when_no_command(capsys):
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "pipeline-scheduler" in captured.out


def test_cli_schedule_outputs_summary(tmp_path, capsys):
    retry_plan_file = tmp_path / "retry_plan.json"
    retry_plan_file.write_text(
        json.dumps(sample_retry_plan()),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "schedule",
            str(retry_plan_file),
            "--generated-at",
            "2026-07-02T20:40:00Z",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Pipeline Scheduler" in captured.out
    assert "Pipeline ID: pipeline-001" in captured.out
    assert "Status: ready" in captured.out
    assert "Total Tasks: 1" in captured.out
    assert "Queued Tasks: 1" in captured.out
    assert "First Run At: 2026-07-02T20:40:20Z" in captured.out


def test_cli_schedule_verbose_outputs_tasks(tmp_path, capsys):
    retry_plan_file = tmp_path / "retry_plan.json"
    retry_plan_file.write_text(
        json.dumps(sample_retry_plan()),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "schedule",
            str(retry_plan_file),
            "--generated-at",
            "2026-07-02T20:40:00Z",
            "--verbose",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Scheduled Tasks" in captured.out
    assert "execute | Execute Pipeline" in captured.out
    assert "attempt=2" in captured.out
    assert "run_at=2026-07-02T20:40:20Z" in captured.out


def test_cli_schedule_empty_retry_plan(tmp_path, capsys):
    retry_plan_file = tmp_path / "retry_plan.json"
    retry_plan_file.write_text(
        json.dumps(
            {
                "pipeline_id": "pipeline-001",
                "policy": {},
                "candidates": [],
                "decisions": [],
                "summary": {},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "schedule",
            str(retry_plan_file),
            "--generated-at",
            "2026-07-02T20:40:00Z",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Status: empty" in captured.out
    assert "Total Tasks: 0" in captured.out


def test_cli_schedule_returns_error_for_missing_file(capsys):
    exit_code = main(["schedule", "missing.json"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error:" in captured.err


def test_cli_schedule_json_writes_report(tmp_path, capsys):
    retry_plan_file = tmp_path / "retry_plan.json"
    output_file = tmp_path / "schedule.json"

    retry_plan_file.write_text(
        json.dumps(sample_retry_plan()),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "schedule",
            str(retry_plan_file),
            "--generated-at",
            "2026-07-02T20:40:00Z",
            "--json",
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "JSON schedule written:" in captured.out
    assert output_file.exists()

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "ready"
    assert payload["summary"]["queued_tasks"] == 1
