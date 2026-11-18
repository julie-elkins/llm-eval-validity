"""Validate the public metadata-only Phase 5 task manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_FAMILY_COUNT = 10
EXPECTED_REPLICATES = (1, 2, 3)
FORBIDDEN_KEYS = {
    "prompt",
    "response",
    "answer_key",
    "reviewer_identity",
    "private_trace",
    "credential",
}


class ManifestError(ValueError):
    """Raised when a Phase 5 manifest violates the public contract."""


def load_manifest(path: Path) -> dict[str, Any]:
    """Load and validate the top-level JSON shape."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"could not read manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError("manifest must be a JSON object")
    return value


def expand_cases(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand family metadata into the deterministic case matrix."""

    families = manifest.get("families")
    replicates = manifest.get("replicates")
    if not isinstance(families, list) or not isinstance(replicates, list):
        raise ManifestError("families and replicates must be arrays")
    cases: list[dict[str, Any]] = []
    for family in families:
        if not isinstance(family, dict):
            raise ManifestError("every family must be an object")
        family_id = family.get("family_id")
        if not isinstance(family_id, str) or not family_id:
            raise ManifestError("every family requires a family_id")
        for replicate in replicates:
            if not isinstance(replicate, int):
                raise ManifestError("replicate values must be integers")
            cases.append(
                {
                    "case_id": f"{family_id}--replicate-{replicate}",
                    "family_id": family_id,
                    "replicate": replicate,
                    "split": (
                        "holdout"
                        if replicate in manifest.get("holdout_replicates", [])
                        else "development"
                    ),
                }
            )
    return cases


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return metadata-only validation results or raise a safe error."""

    if manifest.get("manifest_version") != "phase5-language-grounded-v1":
        raise ManifestError("unsupported manifest_version")
    if manifest.get("status") != "protocol_only":
        raise ManifestError("manifest status must remain protocol_only before execution")
    if manifest.get("data_class") != "synthetic_metadata":
        raise ManifestError("data_class must be synthetic_metadata")
    if manifest.get("private_task_content_required") is not True:
        raise ManifestError("private_task_content_required must be true")
    if manifest.get("task_content_storage") != "local_only":
        raise ManifestError("task_content_storage must be local_only")

    families = manifest.get("families")
    if not isinstance(families, list) or len(families) != EXPECTED_FAMILY_COUNT:
        raise ManifestError(f"manifest must define {EXPECTED_FAMILY_COUNT} families")
    family_ids = [
        family.get("family_id") for family in families if isinstance(family, dict)
    ]
    if len(set(family_ids)) != EXPECTED_FAMILY_COUNT:
        raise ManifestError("family_id values must be unique")

    replicates = tuple(manifest.get("replicates", []))
    if replicates != EXPECTED_REPLICATES:
        raise ManifestError("replicates must be exactly [1, 2, 3]")
    holdout_replicates = tuple(manifest.get("holdout_replicates", []))
    if not holdout_replicates or not set(holdout_replicates).issubset(set(replicates)):
        raise ManifestError("holdout_replicates must be a non-empty subset of replicates")

    forbidden = _find_forbidden_keys(manifest)
    if forbidden:
        raise ManifestError(
            "public manifest contains forbidden content-bearing keys: "
            + ", ".join(sorted(forbidden))
        )

    cases = expand_cases(manifest)
    holdout_count = sum(case["split"] == "holdout" for case in cases)
    if len(cases) != 30:
        raise ManifestError("manifest must expand to exactly 30 cases")
    if holdout_count < 10:
        raise ManifestError("at least one third of cases must be held out")

    return {
        "manifest_version": manifest["manifest_version"],
        "family_count": len(families),
        "replicate_count": len(replicates),
        "case_count": len(cases),
        "holdout_case_count": holdout_count,
        "development_case_count": len(cases) - holdout_count,
        "status": "valid",
        "raw_content_included": False,
    }


def _find_forbidden_keys(value: object) -> set[str]:
    """Find forbidden field names without inspecting content values."""

    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_KEYS:
                found.add(key)
            found.update(_find_forbidden_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(_find_forbidden_keys(nested))
    return found


def main(argv: list[str] | None = None) -> int:
    """Validate a manifest and emit a compact JSON result."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("research/response-quality/PHASE5_TASK_MANIFEST.json"),
    )
    args = parser.parse_args(argv)
    try:
        result = validate_manifest(load_manifest(args.manifest))
    except ManifestError as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
