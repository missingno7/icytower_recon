"""Restore interrupted publication only after the former process has exited."""
import ctypes
import os
from common import ROOT
from publication import restore_journal


def process_alive(pid):
    if pid<=0: raise ValueError('Invalid lock PID')
    if os.name=='nt':
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.restype=ctypes.c_void_p
        api.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
        api.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
        api.CloseHandle.argtypes=[ctypes.c_void_p]
        handle=api.OpenProcess(0x1000,False,pid)
        if not handle:
            if ctypes.get_last_error()==87: return False
            raise ValueError('Cannot establish whether publication owner exited')
        try:
            code=ctypes.c_ulong()
            if not api.GetExitCodeProcess(handle,ctypes.byref(code)): raise ValueError('Cannot inspect publication owner')
            return code.value==259
        finally: api.CloseHandle(handle)
    try: os.kill(pid,0); return True
    except ProcessLookupError: return False


def main():
    lock=ROOT/'build/grinder/promotion.lock'; journal=ROOT/'build/grinder/publication.zip'
    if lock.exists() and process_alive(int(lock.read_text())):
        raise ValueError('Publication owner is still running; recovery refused')
    # Exclusive recovery sentinel prevents two recovery commands racing each other.
    guard=ROOT/'build/grinder/recovery.lock'; guard.parent.mkdir(parents=True,exist_ok=True)
    if guard.exists():
        previous=guard.read_text()
        if process_alive(int(previous)): raise ValueError('Another recovery process is still running')
        if guard.read_text()!=previous: raise ValueError('Recovery owner changed; retry')
        guard.unlink()
    with guard.open('x') as stream: stream.write(str(os.getpid()))
    try:
        if lock.exists() and process_alive(int(lock.read_text())):
            raise ValueError('Publication owner is still running; recovery refused')
        if journal.exists():
            restore_journal(journal,ROOT,ROOT/'docs/current',[
                ROOT/'src/recovery.json',ROOT/'docs/progress.json',ROOT/'docs/blocker-summary.json'])
            print('Restored the previous complete ledger and generated state; task source is retained.')
        else: print('No publication journal; current authoritative files were not changed.')
        lock.unlink(missing_ok=True)
    finally: guard.unlink()
    print('Run the active task verifier, then retry promotion or block the task.')


if __name__=='__main__': main()
