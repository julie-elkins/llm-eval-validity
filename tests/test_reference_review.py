import json

import pytest

from tools.create_reference_review_packet import build_packet
from validity.reference_review import (
    ReviewValidationError,
    compare_forms,
    validate_form,
    validate_packet,
)


def test_packet_is_blinded_and_has_expected_case_count():
    packet, answer_key, form = build_packet()

    assert validate_packet(packet) == tuple(f"review-{index:02d}" for index in range(1, 12))
    assert len(packet["cases"]) == 11
    assert all("source_case" not in case for case in packet["cases"])
    assert all("contract_decision" in case for case in answer_key["cases"])
    assert form["packet_digest"] == packet["packet_digest"]


def test_form_validation_requires_the_packet_digest():
    packet, _, form = build_packet()
    form["packet_digest"] = "wrong"

    with pytest.raises(ReviewValidationError, match="packet digest"):
        validate_form(packet, form)


def test_packet_validation_requires_a_packet_digest():
    packet, _, _ = build_packet()
    del packet["packet_digest"]

    with pytest.raises(ReviewValidationError, match="packet_digest"):
        validate_packet(packet)


def test_form_validation_requires_every_packet_case():
    packet, _, form = build_packet()
    form["judgments"].pop()

    with pytest.raises(ReviewValidationError, match="every packet case"):
        validate_form(packet, form)


def test_two_forms_produce_metadata_only_agreement():
    packet, _, template = build_packet()
    first = json.loads(json.dumps(template))
    second = json.loads(json.dumps(template))
    first["reviewer_id"] = "reviewer-01"
    second["reviewer_id"] = "reviewer-02"
    for row in first["judgments"]:
        row["evidence_sufficient"] = "yes"
    for row in second["judgments"]:
        row["evidence_sufficient"] = "yes"
    second["judgments"][0]["evidence_sufficient"] = "unclear"

    result = compare_forms(packet, [first, second])

    assert result["eligible_form_count"] == 2
    assert result["common_case_count"] == 11
    assert result["reviewer_agreement"]["evidence_sufficient"] == {
        "common_cases": 11,
        "agreements": 10,
        "disagreements": 1,
        "unclear_labels": 1,
    }
    assert "reviewer-01" not in json.dumps(result)
    assert "review-01" not in json.dumps(result)
