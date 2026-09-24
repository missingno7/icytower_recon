from pathlib import Path
import difflib
import re

root = Path(__file__).resolve().parents[3]
folder = Path(__file__).resolve().parent
base = root / "build/tu-context/game-fld-adspot"
labels = {
    "baseline": "research-20260924-http-response-baseline-dumps",
    "comments": "research-20260924-http-response-position-comments-dumps",
}
for suffix in ("181r.csa", "182r.peephole2"):
    streams = {}
    for tag, label in labels.items():
        s = (folder / f"{tag}.{suffix}.txt").read_text(encoding="utf-8")
        path = str(base / label / "overlay/src/fld_adspot.c")
        s = re.sub(re.escape(path) + r":\d+", "<SOURCE>", s)
        streams[tag] = s.splitlines()
    diff = list(difflib.unified_diff(streams["baseline"], streams["comments"], n=2))
    (folder / f"baseline-vs-comments.{suffix}.diff").write_text("\n".join(diff) + "\n", encoding="utf-8")
    print(suffix, "normalized lines", len(streams["baseline"]), len(streams["comments"]), "diff lines", len(diff))
    print("\n".join(diff[:70]))
