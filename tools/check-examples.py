#!/usr/bin/env python3
"""Spec 自驗腳本：schema 本身合法（Draft 2020-12）＋valid 範例必過＋invalid 範例必被拒。

CI 用法：python3 tools/check-examples.py（依賴：jsonschema、pyyaml）
schema 改壞任何一個範例的預期結果即非零退出。
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent

# (schema, fixture, 預期 valid)
CASES = [
    ("schemas/profile.schema.json", "schemas/examples/profile.valid.yaml", True),
    ("schemas/profile.schema.json", "schemas/examples/profile.invalid.yaml", False),
    ("schemas/acceptance.schema.json", "schemas/examples/acceptance.valid.yaml", True),
    ("schemas/acceptance.schema.json", "schemas/examples/acceptance.invalid.yaml", False),
    ("schemas/maintenance.schema.json", "schemas/examples/maintenance.valid.yaml", True),
    ("schemas/maintenance.schema.json", "schemas/examples/maintenance.invalid.yaml", False),
    ("schemas/service-card.schema.json", "schemas/examples/service-card.valid.yaml", True),
    ("schemas/service-card.schema.json", "schemas/examples/service-card.invalid.yaml", False),
    ("verification/evidence-pack.schema.json", "verification/examples/evidence-pack.valid.json", True),
    ("verification/evidence-pack.schema.json", "verification/examples/evidence-pack.invalid.json", False),
]


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def main() -> int:
    failures = []

    schemas = sorted({schema for schema, _, _ in CASES})
    for rel in schemas:
        schema = load(ROOT / rel)
        try:
            Draft202012Validator.check_schema(schema)
            print(f"schema ok    {rel}")
        except Exception as exc:
            failures.append(f"{rel}: schema 本身不合法: {exc}")

    for schema_rel, fixture_rel, expect_valid in CASES:
        validator = Draft202012Validator(load(ROOT / schema_rel))
        errors = list(validator.iter_errors(load(ROOT / fixture_rel)))
        actual_valid = not errors
        mark = "pass" if actual_valid == expect_valid else "FAIL"
        expect_label = "valid" if expect_valid else "invalid"
        print(f"fixture {mark}  {fixture_rel} (expect {expect_label}, errors={len(errors)})")
        if actual_valid != expect_valid:
            detail = "; ".join(e.message for e in errors[:3]) or "no errors raised"
            failures.append(f"{fixture_rel}: expected {expect_label}, got opposite ({detail})")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"\nall checks passed ({len(schemas)} schemas, {len(CASES)} fixtures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
