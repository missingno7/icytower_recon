import hashlib
import json
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[3]
out = pathlib.Path(__file__).resolve().parent / "lexical_cfg_batch"
out.mkdir(parents=True, exist_ok=True)
src = (root / "src/httpget.c").read_text(encoding="utf-8")
start = re.search(r"    \{\n        char \*pOut = linebuf;.*?\n    \}\n(?=    if \(sscanf\(linebuf,)", src, re.S)
if not start:
    raise SystemExit("status-line manual parser block was not found")
helper_call = src[:start.start()] + "    i = extractLine(pHTTPData, iResponseBytesCount, linebuf, sizeof(linebuf));\n" + src[start.end():]

# Keep the historical header-line helper call in every candidate. The only
# controlled differences below are the j lexical scope and loop spelling.
body_start = helper_call.index("HTTPResponse *__attribute__((regparm(2))) extractHTTPResponse(")
variants = {"helper_call_control": helper_call}
variants["manual_parser_control"] = src
old = """        HTTPHeader *header;
        int j;

        i += bytesRead;"""
new = """        HTTPHeader *header;

        i += bytesRead;"""
assert old in helper_call
nested_begin = """        {
            int j;
            if (linebuf[0] == ':') {
                j = 0;
            } else {
                for (j = 1; j < bytesRead; j++) {
                    if (linebuf[j] == ':')
                        break;
                }
            }
            header->pHeader = malloc(j + 1);
            memcpy(header->pHeader, linebuf, j);
            header->pHeader[j] = 0;
            header->pValue = malloc(bytesRead - j - 1);
            memcpy(header->pValue, linebuf + j + 2, bytesRead - j - 2);
            header->pValue[bytesRead - j - 2] = 0;
        }
"""
base_parse = """        if (linebuf[0] == ':') {
            j = 0;
        } else {
            for (j = 1; j < bytesRead; j++) {
                if (linebuf[j] == ':')
                    break;
            }
        }
        header->pHeader = malloc(j + 1);
        memcpy(header->pHeader, linebuf, j);
        header->pHeader[j] = 0;
        header->pValue = malloc(bytesRead - j - 1);
        memcpy(header->pValue, linebuf + j + 2, bytesRead - j - 2);
        header->pValue[bytesRead - j - 2] = 0;
"""
assert old in helper_call and base_parse in helper_call
scope = helper_call.replace(old, new).replace(base_parse, nested_begin)
variants["j_nested_scope"] = scope
variants["j_nested_scope_for_forever"] = scope.replace("for (j = 1; j < bytesRead; j++) {", "for (j = 1; ; j++) {").replace("                    if (linebuf[j] == ':')\n                        break;", "                    if (j >= bytesRead || linebuf[j] == ':')\n                        break;")
variants["j_nested_scope_do_header"] = scope.replace("    while (1) {\n        int bytesRead", "    do {\n        int bytesRead").replace("        }\n    }\n\n    pResponse->iPayloadSize", "        }\n    } while (iResponseBytesCount - i > 0);\n\n    pResponse->iPayloadSize")

compiler = root / "toolchain/tdm-gcc-4.4.1-tdm-2/bin/gcc.exe"
objdump = pathlib.Path(r"C:\msys64\mingw64\bin\objdump.exe")
sys.path.insert(0, str(root / "tools"))
from experiment import compare
results = []
for name, text in variants.items():
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    c, obj = d / "httpget.c", d / "httpget.o"
    dis = d / "object-disasm.txt"
    c.write_text(text, encoding="utf-8", newline="")
    cmd = [str(compiler), "-O2", "-g", "-mfpmath=387", "-DALLEGRO_STATICLINK", "-Iinclude", "-Ithird_party/allegro-4.4.1/include", "-c", str(c), "-o", str(obj)]
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    (d / "compile.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (d / "compile.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    if proc.returncode:
        results.append({"label": name, "returncode": proc.returncode})
        continue
    dump = subprocess.run([str(objdump), "-dr", str(obj)], cwd=root, text=True, capture_output=True, check=True).stdout
    dis.write_text(dump, encoding="utf-8")
    lines, active, code = dump.splitlines(), False, []
    for line in lines:
        if re.search(r"<_?extractHTTPResponse>:$", line.strip()):
            active = True
            continue
        if active and re.match(r"^[0-9a-fA-F]+ <.*>:$", line.strip()):
            break
        if active:
            m = re.match(r"\s*[0-9a-fA-F]+:\s*((?:[0-9a-fA-F]{2}\s+)+)", line)
            if m:
                code.extend(m.group(1).split())
    results.append({"label": name, "returncode": 0, "object_size": obj.stat().st_size,
                    "code_bytes": len(code), "code_sha256": hashlib.sha256(bytes.fromhex("".join(code))).hexdigest(),
                    "source_sha256": hashlib.sha256(c.read_bytes()).hexdigest(),
                    "stderr_lines": proc.stderr.splitlines()[:5]})
    report = compare(obj, r"F:\projects\icytower\trunk\source\httpget.c", root / "assets/icytower15.exe", objdump)
    (d / "strict-diagnostic.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    results[-1]["strict_target_status"] = next(row["status"] for row in report["functions"] if row["name"] == "extractHTTPResponse")
    results[-1]["strict_target_first_difference"] = next(row["first_difference"] for row in report["functions"] if row["name"] == "extractHTTPResponse")
    results[-1]["tu_function_matches"] = report["function_matches"]
    results[-1]["tu_functions_total"] = report["functions_total"]
    results[-1]["exact_neighbor_losses"] = [row["name"] for row in report["functions"] if row["name"] != "extractHTTPResponse" and row["status"] != "FUNCTION_MATCH"]
(out / "probe-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
