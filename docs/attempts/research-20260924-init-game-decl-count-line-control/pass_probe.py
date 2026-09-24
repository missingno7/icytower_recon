"""Verify diagnostic pass dumps do not change either whole-TU object."""

from hashlib import sha256
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from tu_context_probe import build_text, compile_overlay  # noqa: E402


results = {}
for kind in ("control", "blanked"):
    label = f"init-decl-count-{kind}-20260924"
    receipt = json.loads((ROOT / "docs/attempts/tu-context/game-main" / f"{label}.json").read_text())
    spec = {
        "order": "historical",
        "prototypes": "none",
        "research_base": (HERE / f"{kind}.c").relative_to(ROOT).as_posix(),
        "focus": ["init_game", "play"],
    }
    source, _, headers = build_text("game-main", "src/main.c", spec)
    actual_source = sha256(source.encode("cp1252")).hexdigest()
    if actual_source != receipt["overlay_identity"]:
        raise SystemExit(f"{kind}: overlay source differs from strict receipt")
    out, _, _, run = compile_overlay(
        "game-main", "src/main.c", source, label,
        dumps=True, headers=headers,
        extra_flags=("-fdump-tree-all", "-fdump-rtl-expand"),
    )
    if run.returncode:
        raise SystemExit(f"{kind}: diagnostic compile failed: {run.stderr[-2000:]}")
    obj = out / "unit.o"
    dump_sha = sha256(obj.read_bytes()).hexdigest()
    normal_sha = receipt["compiled_object_identity"]["sha256"]
    if dump_sha != normal_sha:
        raise SystemExit(f"{kind}: dump flags changed object: {normal_sha} -> {dump_sha}")
    results[kind] = {
        "label": label,
        "overlay_sha256": actual_source,
        "normal_object_sha256": normal_sha,
        "diagnostic_object_sha256": dump_sha,
        "emission_neutral": True,
        "tree_dump_count": len(list(out.glob("main.c.*t.*"))),
        "expand_dump": str(next(out.glob("main.c.*r.expand")).relative_to(ROOT)).replace("\\", "/"),
    }

(HERE / "pass-neutrality.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
