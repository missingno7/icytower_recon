"""Group retained TU probes by effective function emission, ignoring debug bytes.

Known relocation and same-CU transfer operands are normalized to their symbolic
targets so unrelated TU layout changes do not create false new outcomes. It is a
search aid; only the strict comparison report grants a match.
"""

import argparse
import glob
import hashlib
import json
import re
from pathlib import Path


def effective_identity(function):
    code = bytearray.fromhex("".join(item["bytes"] for item in function["instructions"]))
    if len(code) != function["candidate_size"]:
        raise ValueError("instruction byte coverage differs from function extent")
    relocations = [
        (
            item["function_offset"], item["type"], item["symbol"],
            item["addend"], item.get("target_va"), item.get("resolved_value"),
        )
        for item in function["relocations"]
    ]
    transfers = [
        (
            item["instruction_offset"], item["transfer_kind"],
            item.get("target_function"), item.get("target_va"),
            item.get("candidate_target") if item.get("target_function") is None else None,
        )
        for item in function["direct_transfers"]
    ]
    for item in function["relocations"]:
        start = item["function_offset"]
        code[start:start + 4] = b"\0" * 4
    for item in function["direct_transfers"]:
        start = item["function_offset"]
        size = item["operand_size"]
        code[start:start + size] = b"\0" * size
    payload = json.dumps(
        [code.hex(), relocations, transfers], separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def compiler_response(function, report):
    """Small, mechanical search gradient; the strict report remains authoritative."""
    instructions = function["instructions"]
    branches = sum(
        item["mnemonic"].startswith("j") or item["mnemonic"].startswith("loop")
        for item in instructions
    )
    calls = sum(item["mnemonic"].startswith("call") for item in instructions)
    frame = None
    for item in instructions[:12]:
        m = re.fullmatch(r"sub\s+\$0x([0-9a-f]+),%esp", item["assembly"])
        if m:
            frame = int(m.group(1), 16)
            break
    first = function.get("first_difference")
    return {
        "exact": report["function_matches"],
        "total": report["functions_total"],
        "bytes": f'{function["candidate_size"]}/{function["original_size"]}',
        "first": first.get("offset") if isinstance(first, dict) else None,
        "differing_bytes": len(function["difference_offsets"]),
        "unequal_relocations": sum(not item.get("equal", False) for item in function["relocations"]),
        "frame": f"0x{frame:x}" if frame is not None else "unknown",
        "branches": branches,
        "calls": calls,
        "relocations": len(function["relocations"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="CU target, for example game-main")
    parser.add_argument("function")
    parser.add_argument("--pattern", default="*.json", help="probe label glob")
    parser.add_argument(
        "--compact", action="store_true",
        help="show only the first and latest label for each effective outcome",
    )
    parser.add_argument(
        "--response", action="store_true",
        help="include compact strict and emitted-code metrics for each outcome",
    )
    parser.add_argument(
        "--baseline", help="probe label to compare strict function sets against (with --response)",
    )
    args = parser.parse_args()
    if args.baseline and not args.response:
        parser.error("--baseline requires --response")

    root = Path("docs/attempts/tu-context") / args.target
    groups = {}
    baseline_exact = None
    count = 0
    for path_text in sorted(glob.glob(str(root / args.pattern))):
        path = Path(path_text)
        record = json.loads(path.read_text(encoding="utf-8"))
        report_path = record.get("report_path")
        if not report_path or not Path(report_path).is_file():
            continue
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        function = next(
            (item for item in report["functions"] if item["name"] == args.function),
            None,
        )
        if function is None:
            continue
        identity = effective_identity(function)
        exact = {item["name"] for item in report["functions"]
                 if item["status"] == "FUNCTION_MATCH"} if args.response else None
        if path.stem == args.baseline:
            baseline_exact = exact
        groups.setdefault(identity, []).append(
            (path.stem, function["status"], function["candidate_size"],
             function.get("first_difference"),
             compiler_response(function, report) if args.response else None, exact)
        )
        count += 1

    if args.baseline and baseline_exact is None:
        parser.error("baseline label not found in selected probes: " + args.baseline)

    print(f"{args.target} {args.function}: {count} probes, {len(groups)} effective outcomes")
    for identity, rows in sorted(groups.items(), key=lambda item: item[1][-1][0]):
        if args.compact and len(rows) > 2:
            labels = f"{rows[0][0]}, ... ({len(rows) - 2} others) ..., {rows[-1][0]}"
        else:
            labels = ", ".join(row[0] for row in rows)
        status, size, first = rows[-1][1:4]
        first_offset = first.get("offset") if isinstance(first, dict) else None
        print(f"{identity[:16]}  n={len(rows)}  {status}  size={size}  first={first_offset}")
        statuses = sorted({row[1] for row in rows})
        if len(statuses) > 1:
            print("  strict_statuses=" + ",".join(statuses))
        if args.response:
            response = rows[-1][4]
            print("  exact={exact}/{total} bytes={bytes} diff={differing_bytes} "
                  "unequal_reloc={unequal_relocations}/{relocations} "
                  "frame={frame} branches={branches} calls={calls}".format(**response))
            exact_sets = {frozenset(row[5]) for row in rows}
            if len(exact_sets) > 1:
                print(f"  exact_function_sets={len(exact_sets)} within this target-output group")
            if baseline_exact is not None:
                for row in rows if len(exact_sets) > 1 else rows[-1:]:
                    gained = sorted(row[5] - baseline_exact)
                    lost = sorted(baseline_exact - row[5])
                    label = row[0] + " " if len(exact_sets) > 1 else ""
                    print(f"  {label}vs {args.baseline}: gained={','.join(gained) or '-'} "
                          f"lost={','.join(lost) or '-'}")
        print(f"  {labels}")


if __name__ == "__main__":
    main()
