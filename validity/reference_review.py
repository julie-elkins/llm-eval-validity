"""Validation and aggregate-safe comparison helpers for independent reviews.

Design rules:
1. Require packet and form digests before private artifacts are eligible.
2. Require one judgment for every packet case; partial forms are not analyzable.
3. Emit bounded aggregate counts only, never case text, reviewer identities,
   raw comments, or the answer key.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import hashlib
import json
from typing import Any


JUDGMENT_FIELDS = (
    "evidence_sufficient",
    "classification_supported",
    "required_identifier_present",
    "bounded_workflow_state_supported",
)
# MODELLING ASSUMPTION: these categories are the v2 form's controlled values;
# changing them requires a new form schema and a separately labelled round.
ALLOWED_JUDGMENTS = frozenset({"yes", "no", "unclear"})
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "low"})
ALLOWED_REASONS = frozenset(
    {
        "missing_evidence",
        "unsupported_claim",
        "wrong_classification",
        "ambiguous_rubric",
        "other",
        "",
    }
)


class ReviewValidationError(ValueError):
    """Raised when a private packet or form cannot be safely analyzed."""


def packet_digest(packet: dict[str, Any]) -> str:
    """Return the digest expected for a packet without its stored digest field."""

    body = {key: value for key, value in packet.items() if key != "packet_digest"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_packet(packet: dict[str, Any]) -> tuple[str, ...]:
    """Validate the public-safe shape of a private review packet."""

    required = {
        "schema_version",
        "packet_version",
        "rubric_version",
        "cases",
        "rubric",
        "packet_digest",
    }
    missing = required.difference(packet)
    if missing:
        raise ReviewValidationError(f"packet missing fields: {sorted(missing)}")
    if packet.get("schema_version") != "independent-reference-review-v2":
        raise ReviewValidationError("unsupported packet schema")
    cases = packet["cases"]
    if not isinstance(cases, list) or not 10 <= len(cases) <= 15:
        raise ReviewValidationError("packet must contain 10 to 15 cases")
    ids = []
    for case in cases:
        if set(case) != {
            "case_id",
            "case_kind",
            "question",
            "response",
            "observed_metadata",
            "evidence_contract",
        }:
            raise ReviewValidationError("packet case fields do not match the v2 contract")
        if not isinstance(case["question"], str) or not case["question"].strip():
            raise ReviewValidationError("packet question must be non-empty")
        if not isinstance(case["response"], str) or not case["response"].strip():
            raise ReviewValidationError("packet response must be non-empty")
        ids.append(case["case_id"])
    if len(set(ids)) != len(ids):
        raise ReviewValidationError("packet case IDs must be unique")
    if packet["packet_digest"] != packet_digest(packet):
        raise ReviewValidationError("packet digest does not match packet content")
    return tuple(ids)


def validate_form(packet: dict[str, Any], form: dict[str, Any]) -> tuple[str, ...]:
    """Validate one completed form against the packet without exposing its identity."""

    case_ids = validate_packet(packet)
    if form.get("schema_version") != "independent-reference-review-form-v2":
        raise ReviewValidationError("unsupported form schema")
    if not isinstance(form.get("reviewer_id"), str) or not form["reviewer_id"].strip():
        raise ReviewValidationError("reviewer_id is required in the private form")
    if form.get("packet_version") != packet["packet_version"]:
        raise ReviewValidationError("form packet version does not match packet")
    if form.get("packet_digest") != packet.get("packet_digest"):
        raise ReviewValidationError("form packet digest does not match packet")
    judgments = form.get("judgments")
    if not isinstance(judgments, list):
        raise ReviewValidationError("form judgments must be a list")
    seen = []
    for judgment in judgments:
        expected = {"case_id", *JUDGMENT_FIELDS, "confidence", "disagreement_reason"}
        if set(judgment) != expected:
            raise ReviewValidationError("form judgment fields do not match the v2 contract")
        if judgment["case_id"] not in case_ids:
            raise ReviewValidationError("form contains an unknown case ID")
        for field in JUDGMENT_FIELDS:
            if judgment[field] not in ALLOWED_JUDGMENTS:
                raise ReviewValidationError(f"{field} must be yes, no, or unclear")
        if judgment["confidence"] not in ALLOWED_CONFIDENCE:
            raise ReviewValidationError("confidence must be high, medium, or low")
        if judgment["disagreement_reason"] not in ALLOWED_REASONS:
            raise ReviewValidationError("unknown disagreement reason")
        seen.append(judgment["case_id"])
    if len(set(seen)) != len(seen):
        raise ReviewValidationError("form contains duplicate case judgments")
    if set(seen) != set(case_ids):
        raise ReviewValidationError("form must contain one judgment for every packet case")
    return tuple(seen)


def compare_forms(
    packet: dict[str, Any], forms: list[dict[str, Any]]
) -> dict[str, Any]:
    """Return metadata-only reviewer agreement summaries for eligible forms."""

    case_ids = validate_packet(packet)
    validated = [validate_form(packet, form) for form in forms]
    if not forms:
        raise ReviewValidationError("at least one eligible form is required")
    by_reviewer = {
        form["reviewer_id"]: {row["case_id"]: row for row in form["judgments"]}
        for form in forms
    }
    if len(by_reviewer) != len(forms):
        raise ReviewValidationError("reviewer IDs must be unique in private intake")

    field_summaries: dict[str, dict[str, int]] = {}
    for field in JUDGMENT_FIELDS:
        counts = Counter()
        for first_id, second_id in combinations(by_reviewer, 2):
            common = sorted(set(by_reviewer[first_id]).intersection(by_reviewer[second_id]))
            counts["common_cases"] += len(common)
            counts["agreements"] += sum(
                by_reviewer[first_id][case_id][field]
                == by_reviewer[second_id][case_id][field]
                for case_id in common
            )
            counts["disagreements"] += sum(
                by_reviewer[first_id][case_id][field]
                != by_reviewer[second_id][case_id][field]
                for case_id in common
            )
            counts["unclear_labels"] += sum(
                by_reviewer[first_id][case_id][field] == "unclear"
                or by_reviewer[second_id][case_id][field] == "unclear"
                for case_id in common
            )
        field_summaries[field] = dict(counts)

    return {
        "schema_version": "independent-reference-review-analysis-v1",
        "packet_version": packet["packet_version"],
        "case_count": len(case_ids),
        "eligible_form_count": len(forms),
        "common_case_count": len(
            set.intersection(*(set(review) for review in validated))
        )
        if validated
        else 0,
        "reviewer_agreement": field_summaries,
        "limitation": (
            "This is calibration evidence for the stated packet and rubric; "
            "it is not production safety or model-quality evidence."
        ),
    }
