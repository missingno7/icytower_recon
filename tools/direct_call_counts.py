"""Compare direct-call multiplicities in the original and one compiled CU report.

Call operands are resolved from COFF relocations or decoded same-CU transfers.
This is a topology diagnostic; equal counts never establish function equality.
"""

import argparse
import collections
import json
import re
from pathlib import Path

from common import ROOT
from recovery_pipeline import original_slice


def original_counts(function):
    counts = collections.Counter()
    for insn in original_slice(function["va"], function["original_size"]):
        if not insn["assembly"].startswith("call "):
            continue
        match = re.search(r"<_([^>]+)>", insn["assembly"])
        if match:
            counts[match.group(1)] += 1
    return counts


def candidate_counts(function):
    counts = collections.Counter()
    unresolved = []
    relocations = {row["function_offset"]: row for row in function["relocations"]}
    transfers = {row["instruction_offset"]: row for row in function["direct_transfers"]}
    for insn in function["instructions"]:
        if insn["mnemonic"] != "call" or not insn["bytes"].startswith("e8"):
            continue
        offset = insn["address"] - function["candidate_offset"]
        relocation = relocations.get(offset + 1)
        transfer = transfers.get(offset)
        if relocation:
            name = relocation["symbol"].lstrip("_")
        elif transfer and transfer.get("target_function"):
            name = transfer["target_function"]
        else:
            match = re.search(r"<_([^>]+)>", insn["assembly"])
            name = match.group(1) if match else None
        if name:
            counts[name] += 1
        else:
            unresolved.append((offset, insn["assembly"]))
    return counts, unresolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target")
    parser.add_argument("function")
    parser.add_argument("--report", help="CU comparison JSON; default current verified report")
    args = parser.parse_args()
    path = Path(args.report) if args.report else ROOT / "docs/current/reports" / (args.target + ".json")
    report = json.loads(path.read_text(encoding="utf-8"))
    function = next(row for row in report["functions"] if row["name"] == args.function)
    original = original_counts(function)
    candidate, unresolved = candidate_counts(function)
    print(f"{args.target} {args.function}: original {sum(original.values())}, candidate {sum(candidate.values())} direct calls")
    for name in sorted(set(original) | set(candidate)):
        if original[name] != candidate[name]:
            print(f"{name}: original {original[name]}, candidate {candidate[name]}")
    if unresolved:
        print("unresolved candidate calls:")
        for offset, assembly in unresolved:
            print(f"  +{offset}: {assembly}")


if __name__ == "__main__":
    main()
