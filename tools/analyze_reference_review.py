"""Validate private reviewer forms and emit an aggregate-safe analysis.

Design rules:
1. Read packet and completed forms from private paths supplied by the caller.
2. Write only aggregate-safe comparison metadata to stdout or an explicit file.
3. Never print reviewer identities, case text, raw comments, or the answer key.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validity.reference_review import compare_forms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--form", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    packet = json.loads(args.packet.read_text())
    forms = [json.loads(path.read_text()) for path in args.form]
    result = compare_forms(packet, forms)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
