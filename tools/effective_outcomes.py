"""Group retained TU probes by effective function emission, ignoring debug bytes.

Known relocation and same-CU transfer operands are normalized to their symbolic
targets so unrelated TU layout changes do not create false new outcomes. It is a
search aid; only the strict comparison report grants a match.
"""

import argparse
import glob
import hashlib
import json
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="CU target, for example game-main")
    parser.add_argument("function")
    parser.add_argument("--pattern", default="*.json", help="probe label glob")
    args = parser.parse_args()

    root = Path("docs/attempts/tu-context") / args.target
    groups = {}
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
        groups.setdefault(identity, []).append(
            (path.stem, function["status"], function["candidate_size"],
             function.get("first_difference"))
        )
        count += 1

    print(f"{args.target} {args.function}: {count} probes, {len(groups)} effective outcomes")
    for identity, rows in sorted(groups.items(), key=lambda item: item[1][-1][0]):
        labels = ", ".join(row[0] for row in rows)
        status, size, first = rows[-1][1:]
        first_offset = first.get("offset") if isinstance(first, dict) else None
        print(f"{identity[:16]}  n={len(rows)}  {status}  size={size}  first={first_offset}")
        print(f"  {labels}")


if __name__ == "__main__":
    main()
