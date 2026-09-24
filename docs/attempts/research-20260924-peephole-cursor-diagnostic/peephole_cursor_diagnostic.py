"""Read-only GCC 4.4.1 peephole2 cursor witness from TU probe receipts.

This reconstructs search_ofs *after visible successful scratch choices*.
The RTL-diff extractor cannot see failed searches (which reset search_ofs),
unmaterialized successful searches, or other hidden calls. Therefore an entry
cursor inferred across a gap is conditional, never a compiler-state trace.
"""

import argparse
import json
from pathlib import Path


# GCC 4.4.1 i386 x86_order_regs_for_local_alloc: call-used general registers
# first, then call-saved general registers.  See the research copy at
# build/compiler-research/gcc441-i386.c:26453 and recog.c:2930.
RAW_GENERAL_ORDER = ("ax", "dx", "cx", "bx", "si", "di")
RAW_INDEX = {name: i for i, name in enumerate(RAW_GENERAL_ORDER)}


def summarize(path, focus):
    receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    order = receipt["emission_order"]
    if focus not in order:
        raise ValueError(f"{focus} absent from emission_order in {path}")
    rows = receipt.get("peephole_scratch")
    if not rows:
        raise ValueError(f"{path} lacks peephole_scratch; rerun the isolated TU with dumps")
    names = [row["function"] for row in rows]
    if names != order:
        raise ValueError(f"peephole order differs from emission_order in {path}")
    upto = order.index(focus)
    events = []
    for position, row in enumerate(rows[:upto + 1]):
        for index, reg in enumerate(row["scratch"]):
            if reg not in RAW_INDEX:
                raise ValueError(f"unknown i386 scratch register {reg!r} in {path}")
            events.append({
                "function": row["function"],
                "emission_position": position,
                "within_function": index,
                "observed_register": reg,
                "cursor_after_visible_success": RAW_INDEX[reg] + 1,
            })
    prior = [event for event in events if event["emission_position"] < upto]
    target = [event for event in events if event["emission_position"] == upto]
    return {
        "receipt": str(path),
        "focus": focus,
        "emission_position": upto,
        "prior_visible_events": prior,
        "last_prior_visible_event": prior[-1] if prior else None,
        "target_visible_events": target,
        "conditional_entry_cursor": prior[-1]["cursor_after_visible_success"] if prior else 0,
        "entry_cursor_is_proven": False,
        "reason": "Failed searches reset search_ofs and unmaterialized calls are absent from RTL diffs.",
    }


def compare(left, right):
    a, b = left["prior_visible_events"], right["prior_visible_events"]
    common = 0
    for x, y in zip(a, b):
        if (x["function"], x["observed_register"]) != (y["function"], y["observed_register"]):
            break
        common += 1
    return {
        "common_prior_visible_events": common,
        "prior_visible_sequences_equal": a == b,
        "first_left_difference": a[common] if common < len(a) else None,
        "first_right_difference": b[common] if common < len(b) else None,
        "target_visible_sequences_equal": left["target_visible_events"] == right["target_visible_events"],
        "exact_internal_cursor_comparison_available": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path, help="dump-enabled TU context receipt")
    parser.add_argument("right", type=Path, nargs="?", help="optional second receipt")
    parser.add_argument("--focus", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    left = summarize(args.left, args.focus)
    result = {"left": left}
    if args.right:
        right = summarize(args.right, args.focus)
        result.update(right=right, comparison=compare(left, right))
    output = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
