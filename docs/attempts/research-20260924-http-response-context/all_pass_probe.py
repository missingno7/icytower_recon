"""Diagnostic-only pass dumps for the HTTPResponse owner context."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / "tools"))
from tu_context_probe import compile_overlay
from experiment import compare
from recovery_pipeline import OBJDUMP

folder = Path(__file__).resolve().parent
build_root = root / "build/tu-context/game-fld-adspot"
labels = {
    "baseline": "research-20260924-http-response-baseline",
    "comments": "research-20260924-http-response-position-comments",
}

def effective(report):
    return {
        row["name"]: {
            "status": row["status"],
            "instruction_sha256": hashlib.sha256(bytes.fromhex(
                "".join(ins["bytes"] for ins in row["instructions"])
            )).hexdigest(),
            "relocations": [
                (r["function_offset"], r["symbol"], r["addend"], r["target_va"])
                for r in row["relocations"]
            ],
        }
        for row in report["functions"]
    }

result = {"flags": ["-fdump-tree-optimized", "-fdump-rtl-all"], "cohorts": {}}
for name, old_label in labels.items():
    compiled_overlay = build_root / old_label / "overlay/src/fld_adspot.c"
    source = compiled_overlay.read_bytes().decode("cp1252")
    label = "research-20260924-http-response-" + name + "-all-passes"
    out, reference, build, proc = compile_overlay(
        "game-fld-adspot", "src/fld_adspot.c", source, label,
        dumps=False, cgraph=False,
        extra_flags=("-fdump-tree-optimized", "-fdump-rtl-all"),
    )
    if proc.returncode:
        raise RuntimeError(f"{name} compile failed: {proc.stderr[-2000:]}")
    report = compare(
        out / "unit.o", reference["historical_cu"],
        root / "assets/icytower15.exe", OBJDUMP,
    )
    old_report = json.loads((build_root / old_label / "comparison.json").read_text())
    old_effective = effective(old_report)
    new_effective = effective(report)
    row = next(x for x in report["functions"] if x["name"] == "fldads_get_random_ad")
    result["cohorts"][name] = {
        "source_sha256": hashlib.sha256(source.encode("cp1252")).hexdigest(),
        "dump_dir": str(out.relative_to(root)).replace("\\", "/"),
        "strict_exact": report["function_matches"],
        "all_effective_equal_to_no_dumps": old_effective == new_effective,
        "focus_status": row["status"],
        "focus_instruction_sha256": new_effective["fldads_get_random_ad"]["instruction_sha256"],
        "tree_optimized_dumps": sorted(p.name for p in out.glob("*.optimized")),
        "rtl_dump_count": len([p for p in out.iterdir() if re.search(r"\.\d+r\.", p.name)]),
    }
(folder / "all-pass-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
