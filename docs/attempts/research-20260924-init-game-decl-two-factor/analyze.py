"""Summarize the frozen four corners without changing the strict oracle."""

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from effective_outcomes import effective_identity, compiler_response

labels = {
    "A_neither": "init-decl-count-control-20260924",
    "B_early": "init-decl-two-factor-early-20260924",
    "C_late": "init-decl-two-factor-late-20260924",
    "D_both": "init-decl-count-blanked-20260924",
}
sources = {
    "A_neither": ROOT / "docs/attempts/research-20260924-init-game-decl-count-line-control/control.c",
    "B_early": HERE / "early.c",
    "C_late": HERE / "late.c",
    "D_both": ROOT / "docs/attempts/research-20260924-init-game-decl-count-line-control/blanked.c",
}
source_bytes = {key: path.read_bytes() for key, path in sources.items()}
a = source_bytes["A_neither"]
positions = {key: {i for i, (x, y) in enumerate(zip(a, data)) if x != y}
             for key, data in source_bytes.items()}
assert all(len(data) == len(a) and len(data.splitlines()) == len(a.splitlines())
           for data in source_bytes.values())
assert positions["B_early"].isdisjoint(positions["C_late"])
assert positions["B_early"] | positions["C_late"] == positions["D_both"]


def function_section(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    start = re.search(r"(?m)^;; Function init_game\b", text)
    if start is None:
        raise ValueError(f"init_game absent from {path}")
    nxt = re.search(r"(?m)^;; Function ", text[start.end():])
    end = start.end() + nxt.start() if nxt else len(text)
    return text[start.start():end]


def phi_class(text):
    names = re.findall(r"(?m)^\s*#\s+([A-Za-z][A-Za-z0-9_]*)_\d+\s*=\s*PHI\s*<", text)
    relevant = [name for name in names if name in {"check", "replay_path", "i"}]
    return relevant[:3]


def optimized_order(text):
    forms = {"i": r"(?m)^\s*i = 1;\s*$",
             "check": r"(?m)^\s*check = 0;\s*$",
             "replay_path": r"(?m)^\s*replay_path = 0B;\s*$"}
    hits = {key: re.search(pattern, text) for key, pattern in forms.items()}
    if not all(hits.values()):
        raise ValueError("optimized initialization not found")
    return sorted(forms, key=lambda key: hits[key].start())


def first_instruction_delta(base, variant):
    left, right = base["instructions"], variant["instructions"]
    for i, (x, y) in enumerate(zip(left, right)):
        if (x["bytes"], x["assembly"]) != (y["bytes"], y["assembly"]):
            return {
                "index": i,
                "offset": x["address"] - left[0]["address"],
                "A": x["assembly"],
                "variant": y["assembly"],
            }
    return None


corners = {}
for key, label in labels.items():
    receipt = json.loads((ROOT / "docs/attempts/tu-context/game-main" / f"{label}.json").read_text())
    build = ROOT / "build/tu-context/game-main" / label
    report = json.loads((build / "comparison.json").read_text())
    functions = {f["name"]: f for f in report["functions"]}
    exact = sorted(name for name, f in functions.items() if f["status"] == "FUNCTION_MATCH")
    overlay = (build / "overlay/src/main.c").read_bytes()
    overlay_positions = {i for i, (x, y) in enumerate(zip(a, overlay)) if x != y}
    if overlay_positions != positions[key]:
        raise ValueError(f"{key}: builder changed more than the planned declarations")
    corner = {
        "label": label,
        "source_bytes": len(overlay),
        "source_lines": len(overlay.splitlines()),
        "changed_positions_vs_A": len(positions[key]),
        "source_sha256": receipt["edits"]["research_base"]["identity"]["sha256"],
        "object_sha256": receipt["compiled_object_identity"]["sha256"],
        "compiler": receipt["compiler"],
        "prototypes": receipt["edits"]["prototypes"],
        "exact_count": len(exact),
        "exact_peer_names": exact,
        "gains": receipt["gains"],
        "losses": receipt["losses"],
        "new_implicit_declarations": receipt["new_implicit_declarations"],
        "phi_class_023t_ssa": phi_class(function_section(build / "main.c.023t.ssa")),
        "optimized_order_123t": optimized_order(function_section(build / "main.c.123t.optimized")),
        "init_game": {
            "effective_sha256": effective_identity(functions["init_game"]),
            "strict_status": functions["init_game"]["status"],
            "first_difference": functions["init_game"]["first_difference"],
            "response": compiler_response(functions["init_game"], report),
        },
        "play": {
            "effective_sha256": effective_identity(functions["play"]),
            "strict_status": functions["play"]["status"],
            "first_difference": functions["play"]["first_difference"],
            "response": compiler_response(functions["play"], report),
        },
    }
    corners[key] = corner

a_report = json.loads((ROOT / "build/tu-context/game-main" /
                       labels["A_neither"] / "comparison.json").read_text())
a_functions = {f["name"]: f for f in a_report["functions"]}
for key, label in labels.items():
    report = json.loads((ROOT / "build/tu-context/game-main" / label / "comparison.json").read_text())
    funcs = {f["name"]: f for f in report["functions"]}
    corners[key]["first_init_instruction_delta_vs_A"] = first_instruction_delta(
        a_functions["init_game"], funcs["init_game"])
    corners[key]["first_play_instruction_delta_vs_A"] = first_instruction_delta(
        a_functions["play"], funcs["play"])
    assert corners[key]["exact_peer_names"] == corners["A_neither"]["exact_peer_names"]

result = {
    "position_invariant": True,
    "group_position_disjoint_and_union_equals_both": True,
    "corners": corners,
}
(HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    key: {
        "phi": value["phi_class_023t_ssa"],
        "optimized": value["optimized_order_123t"],
        "init_identity": value["init_game"]["effective_sha256"][:16],
        "init_first_oracle": value["init_game"]["response"]["first"],
        "init_diff_bytes": value["init_game"]["response"]["differing_bytes"],
        "play_identity": value["play"]["effective_sha256"][:16],
        "play_first_oracle": value["play"]["response"]["first"],
        "exact": value["exact_count"],
        "first_init_delta_vs_A": value["first_init_instruction_delta_vs_A"],
    } for key, value in corners.items()
}, indent=2))
