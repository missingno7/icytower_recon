from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
base = root / "build/tu-context/game-fld-adspot"
out = Path(__file__).resolve().parent
labels = {
    "baseline": "research-20260924-http-response-baseline-dumps",
    "position": "research-20260924-http-response-position-preserved-dumps",
    "comments": "research-20260924-http-response-position-comments-dumps",
}
for tag, label in labels.items():
    for suffix in ("181r.csa", "182r.peephole2"):
        path = base / label / ("fld_adspot.c." + suffix)
        text = path.read_text(encoding="utf-8", errors="replace")
        marker = ";; Function fldads_get_random_ad"
        start = text.index(marker)
        match = re.search(r"^;; Function ", text[start + len(marker):], re.M)
        stop = start + len(marker) + match.start() if match else len(text)
        (out / f"{tag}.{suffix}.txt").write_text(text[start:stop], encoding="utf-8")
