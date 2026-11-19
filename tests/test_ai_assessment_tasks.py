import json

import pytest

from tools.validate_ai_assessment_tasks import (
    ManifestValidationError,
    load_manifest,
    validate_manifest,
)


def test_public_ai_assessment_manifest_is_metadata_only():
    manifest = load_manifest()

    assert len(manifest["tasks"]) == 7
    assert validate_manifest(manifest) == tuple(
        task["task_id"] for task in manifest["tasks"]
    )
    assert manifest["answer_keys_included"] is False
    assert manifest["participant_content_included"] is False


def test_public_manifest_rejects_answer_key_fields():
    manifest = load_manifest()
    manifest["tasks"][0]["answer_key"] = "must not be public"

    with pytest.raises(ManifestValidationError, match="forbidden public fields"):
        validate_manifest(manifest)


def test_public_manifest_requires_transfer_form():
    manifest = load_manifest()
    del manifest["tasks"][0]["forms"]["transfer"]

    with pytest.raises(ManifestValidationError, match="baseline, assisted, and transfer"):
        validate_manifest(manifest)


def test_manifest_is_json_serializable_without_hidden_content():
    manifest = load_manifest()
    round_trip = json.loads(json.dumps(manifest))

    assert round_trip == manifest
