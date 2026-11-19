from pathlib import Path

from tools.validate_phase5_manifest import load_manifest, validate_manifest


MANIFEST = (
    Path(__file__).parents[1]
    / "research"
    / "response-quality"
    / "PHASE5_TASK_MANIFEST.json"
)


def test_phase5_manifest_is_a_30_case_metadata_only_matrix():
    result = validate_manifest(load_manifest(MANIFEST))

    assert result == {
        "manifest_version": "phase5-language-grounded-v1",
        "family_count": 10,
        "replicate_count": 3,
        "case_count": 30,
        "holdout_case_count": 10,
        "development_case_count": 20,
        "status": "valid",
        "raw_content_included": False,
    }
