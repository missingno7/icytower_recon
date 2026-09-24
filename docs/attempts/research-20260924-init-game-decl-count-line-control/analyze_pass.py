"""Locate the first observed init_game initialization-order boundary."""

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "build/tu-context/game-main"
control = BASE / "init-decl-count-control-20260924"
blanked = BASE / "init-decl-count-blanked-20260924"


def section(path):
    data = path.read_text(encoding="utf-8", errors="replace")
    found = re.search(r"(?m)^;; Function init_game\b", data)
    if not found:
        return None
    next_function = re.search(r"(?m)^;; Function ", data[found.end():])
    end = found.end() + next_function.start() if next_function else len(data)
    return data[found.start():end]


def order(body):
    forms = {"i": r"(?m)^\s*i = 1;\s*$",
             "check": r"(?m)^\s*check = 0;\s*$",
             "replay_path": r"(?m)^\s*replay_path = 0B;\s*$"}
    found = {name: re.search(pattern, body) for name, pattern in forms.items()}
    if not all(found.values()):
        return None
    return sorted(forms, key=lambda name: found[name].start())


def phi_sequence(body):
    names = re.findall(r"(?m)^\s*#\s+([A-Za-z][A-Za-z0-9_]*)_\d+\s*=\s*PHI\s*<", body)
    return [name for name in names if name in {"i", "check", "replay_path", "checkFile"}]


rows = []
for path in sorted(control.glob("main.c.*t.*")):
    other = blanked / path.name
    if not other.is_file():
        continue
    a, b = section(path), section(other)
    if a is None or b is None:
        continue
    rows.append({
        "pass": path.name,
        "raw_section_equal": a == b,
        "control_order": order(a),
        "blanked_order": order(b),
        "control_phi_count": len(re.findall(r"\bPHI\b", a)),
        "blanked_phi_count": len(re.findall(r"\bPHI\b", b)),
        "control_relevant_phi_sequence": phi_sequence(a),
        "blanked_relevant_phi_sequence": phi_sequence(b),
    })

different = [r for r in rows if r["control_order"] and r["blanked_order"]
             and r["control_order"] != r["blanked_order"]]
result = {
    "tree_passes_compared": len(rows),
    "first_raw_section_difference": next((r["pass"] for r in rows if not r["raw_section_equal"]), None),
    "first_observed_initialization_reorder": different[0]["pass"] if different else None,
    "first_relevant_phi_sequence_difference": next((r["pass"] for r in rows if r["control_relevant_phi_sequence"] != r["blanked_relevant_phi_sequence"]), None),
    "first_reorder_orders": {k: different[0][k] for k in ("control_order", "blanked_order")} if different else None,
    "near_boundary": rows[max(0, rows.index(different[0]) - 5):rows.index(different[0]) + 4] if different else [],
    "optimized": [r for r in rows if r["pass"].endswith("123t.optimized")],
    "ssa": [r for r in rows if r["pass"].endswith("023t.ssa")],
}
original_name = "main.c.003t.original"
original_a = section(control / original_name)
original_b = section(blanked / original_name)
def normalize_generated_labels(body):
    return re.sub(r"\bD\.\d+\b", "D.#", body)
result["original_tree_equal_after_generated_label_normalization"] = (
    normalize_generated_labels(original_a) == normalize_generated_labels(original_b)
)
function_reports = []
for directory in (control, blanked):
    report = json.loads((directory / "comparison.json").read_text(encoding="utf-8"))
    function_reports.append(next(f for f in report["functions"] if f["name"] == "init_game"))
left, right = (f["instructions"] for f in function_reports)
first_instruction = next(i for i, (a, b) in enumerate(zip(left, right))
                         if (a["bytes"], a["assembly"]) != (b["bytes"], b["assembly"]))
result["first_candidate_instruction_difference"] = {
    "index": first_instruction,
    "function_offset": left[first_instruction]["address"] - left[0]["address"],
    "control": [{k: item[k] for k in ("bytes", "assembly")}
                for item in left[first_instruction:first_instruction + 3]],
    "blanked": [{k: item[k] for k in ("bytes", "assembly")}
                for item in right[first_instruction:first_instruction + 3]],
}
(HERE / "pass-order.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
