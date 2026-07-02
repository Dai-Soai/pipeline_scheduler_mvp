import json
from pathlib import Path
from typing import Any


class RetryPlanLoaderError(Exception):
    """Raised when a retry plan cannot be loaded or normalized."""


def load_retry_plan(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise RetryPlanLoaderError(f"retry plan file not found: {path}")

    if not path.is_file():
        raise RetryPlanLoaderError(f"retry plan path is not a file: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except json.JSONDecodeError as error:
        raise RetryPlanLoaderError(f"invalid retry plan JSON: {error}") from error

    if not isinstance(payload, dict):
        raise RetryPlanLoaderError("retry plan root must be a JSON object")

    return normalize_retry_plan(payload)


def normalize_retry_plan(payload: dict[str, Any]) -> dict[str, Any]:
    pipeline_id = payload.get("pipeline_id")
    candidates = payload.get("candidates", [])
    decisions = payload.get("decisions", [])
    policy = payload.get("policy", {})
    summary = payload.get("summary", {})

    if not pipeline_id:
        raise RetryPlanLoaderError("retry plan requires pipeline_id")

    if candidates is None:
        candidates = []

    if decisions is None:
        decisions = []

    if not isinstance(candidates, list):
        raise RetryPlanLoaderError("retry plan candidates must be a list")

    if not isinstance(decisions, list):
        raise RetryPlanLoaderError("retry plan decisions must be a list")

    if not isinstance(policy, dict):
        raise RetryPlanLoaderError("retry plan policy must be an object")

    if not isinstance(summary, dict):
        raise RetryPlanLoaderError("retry plan summary must be an object")

    return {
        "pipeline_id": str(pipeline_id),
        "policy": policy,
        "candidates": candidates,
        "decisions": decisions,
        "summary": summary,
        "metadata": payload.get("metadata", {}),
    }
