from pathlib import Path

build_exe = Path(__file__).resolve().parents[1] / 'build' / 'SOFME' / 'SOFME.exe'
if not build_exe.exists():
    print('MISSING_EXECUTABLE', build_exe)
    raise SystemExit(1)

print('EXECUTABLE', build_exe)
print('SIZE', build_exe.stat().st_size)

terms = [b'python314.dll', b'_internal', b'PYZ-00.pyz', b'base_library.zip', b'_MEI', b'pyimod']
with build_exe.open('rb') as f:
    data = f.read()
for term in terms:
    print(term.decode('latin1'), term in data)
