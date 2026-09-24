"""Verify emission-neutral GCC pass dumps for the two new TU corners."""

from hashlib import sha256
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from tu_context_probe import build_text, compile_overlay

results = {}
for kind in ("early", "late"):
    label = f"init-decl-two-factor-{kind}-20260924"
    receipt_path = ROOT / "docs/attempts/tu-context/game-main" / f"{label}.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    spec = {
        "order": "historical",
        "prototypes": "none",
        "research_base": (HERE / f"{kind}.c").relative_to(ROOT).as_posix(),
        "focus": ["init_game", "play"],
    }
    source, _, headers = build_text("game-main", "src/main.c", spec)
    source_hash = sha256(source.encode("cp1252")).hexdigest()
    if source_hash != receipt["overlay_identity"]:
        raise SystemExit(f"{kind}: generated overlay differs from strict receipt")
    out, _, _, run = compile_overlay(
        "game-main", "src/main.c", source, label,
        dumps=True, headers=headers,
        extra_flags=("-fdump-tree-all", "-fdump-rtl-expand"),
    )
    if run.returncode:
        raise SystemExit(f"{kind}: GCC failed: {run.stderr[-2000:]}")
    dumped_hash = sha256((out / "unit.o").read_bytes()).hexdigest()
    normal_hash = receipt["compiled_object_identity"]["sha256"]
    if dumped_hash != normal_hash:
        raise SystemExit(f"{kind}: diagnostic flags changed object")
    results[kind] = {
        "overlay_sha256": source_hash,
        "no_dump_object_sha256": normal_hash,
        "dump_object_sha256": dumped_hash,
        "emission_neutral": True,
        "tree_dump_count": len(list(out.glob("main.c.*t.*"))),
    }
(HERE / "pass-neutrality.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
