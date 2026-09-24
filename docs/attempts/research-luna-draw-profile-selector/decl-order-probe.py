import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ATTEMPT = ROOT / "docs/attempts/research-luna-draw-profile-selector"
BASE = ATTEMPT / "overlay/typed_row_and_extent_locals.c"
OUT = ATTEMPT / "build/historical_top_level_decl_order"
OUT.mkdir(parents=True, exist_ok=True)

text = BASE.read_text(encoding="cp1252")
old = """    int fh;
    int fg;
    double view_percentage;
    double view_offset;
    int i;
    int profile_index;
    int row_y;
    int width;
    int height;
    int scrollHeight;
    char *profile_name;
    char *current;"""
new = """    int fh;
    int i;
    int fg;
    double view_percentage;
    int width;
    int height;
    int scrollHeight;
    double view_offset;
    int profile_index;
    int row_y;
    char *profile_name;
    char *current;"""
assert text.count(old) == 1
overlay = OUT / "unit.c"
overlay.write_bytes(text.replace(old, new).encode("cp1252"))

prov = json.loads((ATTEMPT / "build/typed_row_and_extent_locals/build-provenance.json").read_text())
cmd = list(prov["command"])
def after(flag, value):
    cmd[cmd.index(flag) + 1] = str(value)
after("-MF", OUT / "unit.d")
after("-aux-info", OUT / "interfaces.aux")
after("-c", overlay)
after("-o", OUT / "unit.o")
proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
(OUT / "compiler.stdout.txt").write_text(proc.stdout, encoding="utf-8")
(OUT / "compiler.stderr.txt").write_text(proc.stderr, encoding="utf-8")
if proc.returncode:
    raise SystemExit(proc.returncode)

sys.path.insert(0, str(ROOT / "tools"))
from experiment import compare
from recovery_pipeline import OBJDUMP
from common import write_json
report = compare(OUT / "unit.o", prov["historical_cu"], ROOT / "assets/icytower15.exe", OBJDUMP)
write_json(OUT / "comparison.json", report)
(OUT / "build-provenance.json").write_text(json.dumps({"compiler": prov["compiler"], "flags": prov["flags"], "command": cmd, "cwd": str(ROOT), "variant": "historical_top_level_decl_order", "base_overlay": str(BASE)}, indent=2) + "\n")
funcs = {f["name"]: f for f in report["functions"]}
print(json.dumps({
    "variant": "historical_top_level_decl_order",
    "draw_profile_selector": {"status": funcs["draw_profile_selector"]["status"], "candidate_size": funcs["draw_profile_selector"]["candidate_size"], "original_size": funcs["draw_profile_selector"]["original_size"], "first_difference": funcs["draw_profile_selector"].get("first_difference")},
    "select_profile": {"status": funcs["select_profile"]["status"], "candidate_size": funcs["select_profile"]["candidate_size"], "original_size": funcs["select_profile"]["original_size"], "first_difference": funcs["select_profile"].get("first_difference")},
    "exact_functions": sorted(n for n, f in funcs.items() if f["status"] == "FUNCTION_MATCH"),
    "function_matches": report.get("function_matches"),
    "whole_text_contribution_equal": report.get("whole_text_contribution_equal"),
}, indent=2))
