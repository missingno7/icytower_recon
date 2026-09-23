"""Isolated, source-equivalent zero-collision guard probes for GCC 4.4.1."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
source = (ROOT / "src/main.c").read_text(encoding="utf-8")
start = source.index("void handle_player_collision_original(int lastX, int lastY)\n{")
end = source.index("\nvoid fadeIn(", start)
body = source[start:end]
old = """        if (ply[player_id]->status==2 || ply[player_id]->status==0)
            ply[player_id]->status=3;
        return;"""
assert body.count(old) == 1

variants = {
    "nested-zero": """        if (ply[player_id]->status!=2) {
            if (ply[player_id]->status==0)
                ply[player_id]->status=3;
        } else {
            ply[player_id]->status=3;
        }
        return;""",
    "split-zero": """        if (ply[player_id]->status==2)
            ply[player_id]->status=3;
        else if (ply[player_id]->status==0)
            ply[player_id]->status=3;
        return;""",
    "inverted-zero": """        if (ply[player_id]->status!=2 && ply[player_id]->status!=0)
            return;
        ply[player_id]->status=3;
        return;""",
}

# The historical branch at +0x170 reaches the same edge-zero store as the
# no-solid branch, while the current compiler lowers their shared value to
# setne. Test an explicit join in a separate, source-equivalent candidate.
tail_old = """        if (solid1==solid2) {
            ply[player_id]->edge=0;
            return;
        }
        ply[player_id]->edge=1;
        return;
    }
    if (solid2) {
        ply[player_id]->y-=solid2-9999;
        ply[player_id]->rotate=0;
        ply[player_id]->edge=2;
        return;
    }
    ply[player_id]->rotate=0;
    ply[player_id]->edge=0;"""
tail_join = """        if (solid1==solid2)
            goto edge_zero;
        ply[player_id]->edge=1;
        return;
    }
    if (solid2) {
        ply[player_id]->y-=solid2-9999;
        ply[player_id]->rotate=0;
        ply[player_id]->edge=2;
        return;
    }
    ply[player_id]->rotate=0;
edge_zero:
    ply[player_id]->edge=0;"""
assert body.count(tail_old) == 1
variants["joined-edge-zero"] = None

results = []
for name, replacement in variants.items():
    candidate = HERE / f"{name}.c"
    variant_body = body.replace(tail_old, tail_join) if replacement is None else body.replace(old, replacement)
    candidate.write_text(variant_body, encoding="utf-8")
    label = f"research-collision-original-{name}-20260923"
    receipt = ROOT / "docs/attempts/tu-context/game-main" / f"{label}.json"
    if receipt.exists():
        data = json.loads(receipt.read_text(encoding="utf-8"))
        results.append({"variant": name, "receipt": receipt.relative_to(ROOT).as_posix(),
                        "focus": data.get("focus"), "gains": data.get("gains"), "losses": data.get("losses")})
        continue
    command = [
        sys.executable, "tools/tu_context_probe.py", "game-main", "src/main.c",
        label, "--order", "current", "--no-prototypes", "--no-dumps",
        "--body", f"handle_player_collision_original={candidate.relative_to(ROOT).as_posix()}",
        "--focus", "handle_player_collision_original",
    ]
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (HERE / f"{name}.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    if run.returncode:
        results.append({"variant": name, "exit": run.returncode, "log": str(HERE / f"{name}.log")})
        continue
    data = json.loads(receipt.read_text(encoding="utf-8"))
    results.append({
        "variant": name,
        "receipt": receipt.relative_to(ROOT).as_posix(),
        "summary": data.get("summary"),
        "focus": data.get("focus"),
        "object": data.get("object"),
    })

(HERE / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
