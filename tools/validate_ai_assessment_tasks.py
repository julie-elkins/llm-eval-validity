"""Validate the public metadata-only AI-assessment task manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MANIFEST_PATH = (
    Path(__file__).parents[1]
    / "research"
    / "ai-assessment-learning"
    / "tasks"
    / "manifest.json"
)

REQUIRED_TASK_FIELDS = {
    "task_id",
    "task_family",
    "target_skill",
    "learning_objective",
    "allowed_evidence",
    "assistance_boundary",
    "forms",
    "rubric_dimensions",
    "expected_failure_modes",
    "public_reason_code",
}

REQUIRED_FORM_NAMES = {"baseline", "assisted", "transfer"}
REQUIRED_TASK_FAMILIES = {
    "concept_application",
    "evidence_interpretation",
    "procedure_or_troubleshooting",
}
REQUIRED_FAILURE_MODES = {
    "evidence_complete",
    "fluent_but_unsupported",
    "correct_answer_wrong_justification",
    "stale_or_contradictory_evidence",
    "ambiguous_requires_uncertainty",
    "useful_assistance_without_transfer_completion",
    "polished_negative_control",
}

# These fields would turn a public task manifest into an answer key or participant
# data store. They are deliberately rejected even if nested in a task object.
FORBIDDEN_FIELDS = {
    "answer",
    "answer_key",
    "expected_answer",
    "expected_disposition",
    "participant_answer",
    "participant_id",
    "reviewer_id",
    "raw_response",
}


class ManifestValidationError(ValueError):
    """Raised when the public task manifest violates the study boundary."""


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(key)
            keys.update(_walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(_walk_keys(nested))
    return keys


def validate_manifest(manifest: dict[str, Any]) -> tuple[str, ...]:
    """Return task identifiers after validating the public manifest."""

    if manifest.get("answer_keys_included") is not False:
        raise ManifestValidationError("answer keys must be explicitly excluded")
    if manifest.get("participant_content_included") is not False:
        raise ManifestValidationError("participant content must be explicitly excluded")

    forbidden = _walk_keys(manifest) & FORBIDDEN_FIELDS
    if forbidden:
        raise ManifestValidationError(
            f"forbidden public fields present: {', '.join(sorted(forbidden))}"
        )

    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ManifestValidationError("tasks must be a non-empty list")

    identifiers: list[str] = []
    families: set[str] = set()
    failure_modes: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ManifestValidationError("each task must be an object")
        missing = REQUIRED_TASK_FIELDS - set(task)
        if missing:
            raise ManifestValidationError(
                f"{task.get('task_id', '<unknown>')} missing: {', '.join(sorted(missing))}"
            )
        task_id = task["task_id"]
        if not isinstance(task_id, str) or not task_id:
            raise ManifestValidationError("task_id must be a non-empty string")
        if task_id in identifiers:
            raise ManifestValidationError(f"duplicate task_id: {task_id}")
        identifiers.append(task_id)
        families.add(task["task_family"])
        failure_modes.update(task["expected_failure_modes"])
        if set(task["forms"]) != REQUIRED_FORM_NAMES:
            raise ManifestValidationError(
                f"{task_id} must define baseline, assisted, and transfer forms"
            )
        if not all(isinstance(value, str) and value for value in task["forms"].values()):
            raise ManifestValidationError(f"{task_id} contains an empty form identifier")

    missing_families = REQUIRED_TASK_FAMILIES - families
    if missing_families:
        raise ManifestValidationError(
            f"task families missing: {', '.join(sorted(missing_families))}"
        )

    # The public task set must carry explicit negative controls. These labels are
    # reason codes, not answer keys, and are safe for the learner-facing manifest.
    if "polished_negative_control" not in failure_modes:
        raise ManifestValidationError("polished negative control is missing")
    if "fluent_but_unsupported" not in failure_modes:
        raise ManifestValidationError("fluent-but-unsupported control is missing")

    return tuple(identifiers)


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    """Load and validate the checked-in manifest."""

    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    validate_manifest(manifest)
    return manifest


if __name__ == "__main__":
    loaded = load_manifest()
    print(f"validated {len(loaded['tasks'])} public AI-assessment task definitions")
