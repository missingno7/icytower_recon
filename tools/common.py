"""Small, dependency-free utilities shared by the reconstruction tools."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TC = ROOT / 'toolchain/tdm-gcc-4.4.1'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def identity(path):
    path = Path(path)
    data = path.read_bytes()
    return {'size': len(data), 'sha256': sha(data)}

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode('utf-8'))

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def run(args, output=None, cwd=ROOT, toolchain=TC):
    env = os.environ.copy()
    env['PATH'] = str(toolchain / 'bin') + os.pathsep + env.get('PATH', '')
    result = subprocess.run([str(x) for x in args], cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f'{args}:\n{result.stderr.decode(errors="replace")}')
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_bytes(result.stdout)
    return result.stdout.decode('utf-8', errors='replace')
