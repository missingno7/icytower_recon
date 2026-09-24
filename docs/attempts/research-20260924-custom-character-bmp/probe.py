"""Isolated strict source-shape probes for load_character_bmp."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from build import COMPILERS, verify_inputs
from binary import Binary
from common import identity, run, write_json
from experiment import compare
from recovery_pipeline import fresh_verify, OBJDUMP, verifier_identity

OUT = Path(__file__).resolve().parent
BUILD = (ROOT / "build/research-20260924-custom-bmp").resolve()
baseline = fresh_verify("game-custom", dest=BUILD / "reference")
base_command = baseline["build"]["command"]
source = (ROOT / "src/custom.c").read_text(encoding="cp1252")
fixture_id = identity(ROOT / "assets/icytower15.exe")
tool_identity = verifier_identity()

variants = {
    "baseline": source,
    # The historical first null branch targets an interior block at +0x56d.
    # Test whether a shared explicit NULL epilogue changes GCC's block layout.
    "shared_null_epilogue": source.replace(
        'if (!fp) { log2file("Could not open %s", filename); return NULL; }',
        'if (!fp) { log2file("Could not open %s", filename); goto null_result; }',
    ).replace("    return NULL;\n}", "null_result:\n    return NULL;\n}"),
    # Make all NULL returns converge on the same labeled endpoint, including
    # the frame/datafile error exits, as a distinct sharing hypothesis.
}

start = source.index("BITMAP *load_character_bmp")
end = source.index("\nint init_custom", start)
body = source[start:end]
shared = body.rsplit("\n}", 1)[0]
shared = shared.replace(
    'if (!fp) { log2file("Could not open %s", filename); return NULL; }',
    'if (!fp) { log2file("Could not open %s", filename); goto null_result; }',
).replace("return NULL;", "goto null_result;")
shared += "\nnull_result:\n    return NULL;\n}"
variants["all_null_exits_shared"] = source[:start] + shared + source[end:]

rows = []
fingerprints = {}
for name, text in variants.items():
    if text == source and name != "baseline":
        rows.append({"variant": name, "state": "NO_SOURCE_CHANGE"})
        continue
    folder = BUILD / name
    folder.mkdir(parents=True, exist_ok=True)
    copy = folder / "probe.c"
    copy.write_bytes(text.encode("cp1252"))
    command = list(base_command)
    for flag, value in [
        ("-MF", folder / "unit.d"),
        ("-aux-info", folder / "interfaces.aux"),
        ("-c", copy),
        ("-o", folder / "unit.o"),
    ]:
        command[command.index(flag) + 1] = str(value)
    command[1:1] = ["-I" + str((ROOT / "src").resolve())]
    run(command, toolchain=COMPILERS["tdm-2"])
    report = compare(folder / "unit.o", baseline["historical_cu"],
                     ROOT / "assets/icytower15.exe", OBJDUMP)
    row = next(item for item in report["functions"]
               if item["name"] == "load_character_bmp")
    obj = Binary(folder / "unit.o")
    text_section = next(section for section in obj.sections
                        if section["name"] == ".text")
    text_bytes = obj.section_bytes(text_section)
    function_symbol = next(symbol for symbol in obj.symbols
                           if symbol["name"] == "_load_character_bmp")
    function_bytes = text_bytes[function_symbol["value"]:
                                function_symbol["value"] + row["candidate_size"]]
    fingerprint = identity(folder / "unit.o")["sha256"]
    code_fingerprint = __import__("hashlib").sha256(function_bytes).hexdigest()
    fingerprints.setdefault(code_fingerprint, []).append(name)
    rows.append({
        "variant": name,
        "source": copy.relative_to(ROOT).as_posix(),
        "source_sha256": identity(copy)["sha256"],
        "object_sha256": fingerprint,
        "function_text_sha256": code_fingerprint,
        "status": row["status"],
        "difference_class": row.get("difference_class"),
        "candidate_size": row.get("candidate_size"),
        "historical_size": row.get("original_size"),
        "first_difference": row.get("first_difference"),
        "difference_offsets": row.get("difference_offsets", []),
        "function_matches": report["function_matches"],
        "object_size": len((folder / "unit.o").read_bytes()),
    })
    print(name, row["status"], row.get("candidate_size"),
          row.get("first_difference"), flush=True)

for path, expected in baseline["build"]["local_inputs"].items():
    if identity(ROOT / path) != expected:
        raise RuntimeError("Maintained input changed during isolated probe: " + path)
verify_inputs("tdm-2")
if identity(ROOT / "assets/icytower15.exe") != fixture_id:
    raise RuntimeError("Historical fixture changed during isolated probe")
if verifier_identity() != tool_identity:
    raise RuntimeError("Verifier changed during isolated probe")

write_json(OUT / "results.json", {
    "scope": "Scratch-only strict compiler experiments; no maintained source or proof changes.",
    "target": "game-custom:load_character_bmp",
    "historical_va": "0x4031cc",
    "historical_size": 1992,
    "compiler": "tdm-2 GCC 4.4.1",
    "flags": baseline["build"]["flags"],
    "fixture_sha256": fixture_id["sha256"],
    "variants": rows,
    "deduplicated_object_groups": list(fingerprints.values()),
})
