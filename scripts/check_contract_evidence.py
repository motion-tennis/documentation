"""Read-only freshness checks for saved S0 evidence, using the standard library."""

import hashlib
import json
from pathlib import Path


def contract_sources(root):
    paths = {root / "spec/motion.proto", root / "spec/reference-profile.json",
             root / "scripts/match_contract.py"}
    for name in ("scripts/contract", "tests/contract", "tests/match"):
        paths.update(path for path in (root / name).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts
                     and path.suffix != ".pyc")
    return {str(path.relative_to(root)): path for path in paths}


def evidence_errors(root):
    root = Path(root).resolve()
    report_path = root / "evidence/s0-contract-report.json"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return ["Cannot read S0 evidence: " + str(error)]
    if not isinstance(report, dict):
        return ["S0 evidence must be an object"]
    errors = []
    if report.get("status") != "passed_offline_contract_checks":
        errors.append("S0 evidence does not record a complete offline contract pass")
    semantic = report.get("semantic_checks", {})
    if not isinstance(semantic, dict) or semantic.get("status") != "passed" or not isinstance(
            semantic.get("tests"), int) or semantic["tests"] <= 0:
        errors.append("S0 evidence lacks passing semantic tests")
    sources = contract_sources(root)
    recorded = report.get("source_sha256", {})
    if not isinstance(recorded, dict):
        return errors + ["S0 source hash manifest must be an object"]
    if set(recorded) != set(sources):
        errors.append("S0 evidence source inventory is stale")
    for name, path in sorted(sources.items()):
        if not path.is_file():
            errors.append("Missing contract source: " + name)
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if recorded.get(name) != actual:
            errors.append("Stale S0 evidence hash: " + name)
        top_level = {"spec/motion.proto": "schema_sha256",
                     "spec/reference-profile.json": "profile_sha256"}.get(name)
        if top_level and report.get(top_level) != actual:
            errors.append("Stale S0 evidence identity: " + top_level)
    return errors
