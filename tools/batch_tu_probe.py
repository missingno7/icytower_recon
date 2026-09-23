#!/usr/bin/env python3
"""Run and summarize a small set of diagnostic TU body-overlay probes.

The strict verifier remains authoritative. This wrapper only delegates to
tu_context_probe.py and summarizes its saved receipts/reports.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import tu_context_probe as context_probe

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "tu_context_probe.py"
RECEIPTS = ROOT / "docs" / "attempts" / "tu-context"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def root_path(value):
    path = Path(value)
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def load_manifest(path):
    data = read_json(path)
    required = ("target", "source", "function", "probes")
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError("manifest missing: " + ", ".join(missing))
    probes = data["probes"]
    if not isinstance(probes, list) or len(probes) < 2:
        raise ValueError("manifest must contain at least two named probes")
    labels, names = set(), set()
    for item in probes:
        if not all(item.get(key) for key in ("name", "label", "body")):
            raise ValueError("each probe requires name, label, and body")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", item["label"]):
            raise ValueError("unsafe probe label: " + item["label"])
        if item["label"] in labels or item["name"] in names:
            raise ValueError("probe names and labels must be unique")
        labels.add(item["label"]); names.add(item["name"])
        body = root_path(item["body"])
        if not body.is_file():
            raise ValueError("body overlay not found: " + str(body))
        item["body_path"] = body
    return data


def body_identity(path):
    content = path.read_bytes()
    return {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def receipt_for(target, label):
    return RECEIPTS / target / (label + ".json")


def cached_receipt(manifest, probe):
    path = receipt_for(manifest["target"], probe["label"])
    if not path.is_file():
        return None
    record = read_json(path)
    if record.get("target") != manifest["target"] or record.get("source") != manifest["source"] or record.get("label") != probe["label"]:
        raise ValueError("existing receipt identity conflicts with manifest: " + str(path))
    source = root_path(manifest["source"])
    if record.get("source_identity") != body_identity(source):
        raise ValueError("existing receipt source identity differs; refusing stale context: " + str(path))
    body = (record.get("edits", {}).get("bodies", {}) or {}).get(manifest["function"])
    if not body or body.get("identity") != body_identity(probe["body_path"]):
        raise ValueError("existing receipt body identity differs; refusing to overwrite: " + str(path))
    recorded_path = root_path(body.get("path", ""))
    if recorded_path != probe["body_path"]:
        raise ValueError("existing receipt body path differs; refusing to reuse: " + str(path))
    order = manifest.get("order", "current")
    if order not in ("current", "historical"):
        order = read_json(root_path(order))
    spec = {
        "order": order,
        "bodies": {manifest["function"]: str(probe["body_path"])},
        "prototypes": "none" if manifest.get("no_prototypes", True) else "auto",
    }
    overlay, _, _ = context_probe.build_text(manifest["target"], manifest["source"], spec)
    if record.get("overlay_identity") != hashlib.sha256(overlay.encode("cp1252")).hexdigest():
        raise ValueError("existing receipt overlay context differs; refusing reuse: " + str(path))
    return path, record


def run_probe(manifest, probe):
    receipt_path = receipt_for(manifest["target"], probe["label"])
    output_dir = ROOT / "build" / "tu-context" / manifest["target"] / probe["label"]
    if receipt_path.exists() or output_dir.exists():
        raise ValueError("probe label already has artifacts but no reusable receipt: " + probe["label"])
    command = [
        sys.executable, str(PROBE), manifest["target"], manifest["source"], probe["label"],
        "--order", manifest.get("order", "current"),
        "--body", manifest["function"] + "=" + str(probe["body_path"]),
        "--focus", manifest["function"], "--no-dumps",
    ]
    if manifest.get("no_prototypes", True):
        command.append("--no-prototypes")
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        raise RuntimeError("tu_context_probe.py failed for " + probe["name"])
    cached = cached_receipt(manifest, probe)
    if cached is None:
        raise RuntimeError("probe succeeded but did not write expected receipt: " + str(receipt_path))
    return cached


def report_row(manifest, probe, receipt):
    record = receipt
    report_path = root_path(record["report_path"])
    if not report_path.is_file():
        raise ValueError("comparison report missing: " + str(report_path))
    report = read_json(report_path)
    target = next((row for row in report.get("functions", []) if row.get("name") == manifest["function"]), None)
    if target is None:
        raise ValueError("strict comparison missing target function: " + manifest["function"])
    if not target.get("instructions"):
        raise ValueError("strict comparison lacks target instruction evidence")
    helper_path = ROOT / "tools" / "effective_outcomes.py"
    spec = importlib.util.spec_from_file_location("effective_outcomes", helper_path)
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    identity = helper.effective_identity(target)
    first = target.get("first_difference")
    return {
        "name": probe["name"], "label": probe["label"], "receipt": str(receipt_for(manifest["target"], probe["label"]).relative_to(ROOT)).replace("\\", "/"),
        "status": target.get("status"), "candidate_size": target.get("candidate_size"), "original_size": target.get("original_size"),
        "first_mismatch": first.get("offset") if isinstance(first, dict) else None,
        "matches_after": record.get("matches_after"), "gains": record.get("gains", []), "losses": record.get("losses", []),
        "effective_identity": identity,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="JSON manifest with 2–4 candidate overlays")
    parser.add_argument("--reuse-only", action="store_true", help="summarize saved receipts; never compile")
    args = parser.parse_args()
    manifest_path = root_path(args.manifest)
    manifest = load_manifest(manifest_path)
    rows = []
    for probe in manifest["probes"]:
        cached = cached_receipt(manifest, probe)
        if cached is None:
            if args.reuse_only:
                raise FileNotFoundError("saved receipt not found for " + probe["label"])
            cached = run_probe(manifest, probe)
        _, record = cached
        rows.append(report_row(manifest, probe, record))
    groups = {}
    for row in rows:
        groups.setdefault(row["effective_identity"], []).append(row["name"])
    print("\nBATCH SUMMARY")
    print(f"{manifest['target']} / {manifest['function']}: {len(rows)} probes, {len(groups)} effective outcomes")
    for row in rows:
        print(f"{row['name']}: {row['status']} size={row['candidate_size']}/{row['original_size']} first={row['first_mismatch']} matches={row['matches_after']} gains={row['gains']} losses={row['losses']}")
    print("effective outcome groups:")
    for identity, names in groups.items():
        print(f"  {identity[:16]}: {', '.join(names)}")
    print("summary_json=" + json.dumps({"target": manifest["target"], "function": manifest["function"], "probes": rows, "effective_groups": groups}, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, FileNotFoundError, KeyError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
