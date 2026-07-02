import json

import pytest

from pipeline_scheduler.loader import (
    RetryPlanLoaderError,
    load_retry_plan,
    normalize_retry_plan,
)


def test_load_retry_plan_from_file(tmp_path):
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

    payload = load_retry_plan(retry_plan_file)

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["policy"] == {}
    assert payload["candidates"] == []
    assert payload["decisions"] == []
    assert payload["summary"] == {}


def test_load_retry_plan_rejects_missing_file(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(RetryPlanLoaderError):
        load_retry_plan(missing_file)


def test_load_retry_plan_rejects_invalid_json(tmp_path):
    retry_plan_file = tmp_path / "bad.json"
    retry_plan_file.write_text("{bad-json", encoding="utf-8")

    with pytest.raises(RetryPlanLoaderError):
        load_retry_plan(retry_plan_file)


def test_load_retry_plan_rejects_non_object_json(tmp_path):
    retry_plan_file = tmp_path / "list.json"
    retry_plan_file.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(RetryPlanLoaderError):
        load_retry_plan(retry_plan_file)


def test_normalize_retry_plan_defaults_optional_lists():
    payload = normalize_retry_plan(
        {
            "pipeline_id": "pipeline-001",
            "candidates": None,
            "decisions": None,
            "policy": {},
            "summary": {},
        }
    )

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["candidates"] == []
    assert payload["decisions"] == []


def test_normalize_retry_plan_rejects_missing_pipeline_id():
    with pytest.raises(RetryPlanLoaderError):
        normalize_retry_plan(
            {
                "policy": {},
                "candidates": [],
                "decisions": [],
                "summary": {},
            }
        )


def test_normalize_retry_plan_rejects_invalid_candidates_type():
    with pytest.raises(RetryPlanLoaderError):
        normalize_retry_plan(
            {
                "pipeline_id": "pipeline-001",
                "candidates": {},
                "decisions": [],
                "policy": {},
                "summary": {},
            }
        )


def test_normalize_retry_plan_rejects_invalid_decisions_type():
    with pytest.raises(RetryPlanLoaderError):
        normalize_retry_plan(
            {
                "pipeline_id": "pipeline-001",
                "candidates": [],
                "decisions": {},
                "policy": {},
                "summary": {},
            }
        )


def test_normalize_retry_plan_rejects_invalid_policy_type():
    with pytest.raises(RetryPlanLoaderError):
        normalize_retry_plan(
            {
                "pipeline_id": "pipeline-001",
                "candidates": [],
                "decisions": [],
                "policy": [],
                "summary": {},
            }
        )


def test_normalize_retry_plan_rejects_invalid_summary_type():
    with pytest.raises(RetryPlanLoaderError):
        normalize_retry_plan(
            {
                "pipeline_id": "pipeline-001",
                "candidates": [],
                "decisions": [],
                "policy": {},
                "summary": [],
            }
        )
