import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist' / 'SOFME'
BUILD = ROOT / 'build' / 'SOFME'


def ensure_runtime_structure():
    # The installer payload must be built from the actual PyInstaller runtime dist output,
    # not from the intermediate PyInstaller build folder. The runtime dist folder contains
    # the Python DLLs such as python314.dll and Qt runtime libraries that are required.
    if not DIST.exists():
        raise FileNotFoundError(
            f"PyInstaller runtime directory not found: {DIST}. "
            "Run `pyinstaller SOFME.spec` first and use the generated dist/SOFME folder."
        )

    internal_dir = DIST / '_internal'
    python_dll_exists = (DIST / 'python314.dll').exists() or (internal_dir / 'python314.dll').exists()
    if not python_dll_exists:
        raise FileNotFoundError(
            f"Expected runtime Python DLL not found in {DIST}. "
            "The current folder is not a valid PyInstaller one-dir output. "
            "Build with `pyinstaller SOFME.spec` and try again."
        )

    # Some PyInstaller layouts keep the Python DLL inside _internal.
    # If the installer payload lacks a root python314.dll, copy it from _internal.
    for dll_name in ('python314.dll', 'python3.dll'):
        source_dll = internal_dir / dll_name
        target_dll = DIST / dll_name
        if source_dll.exists() and not target_dll.exists():
            shutil.copy2(source_dll, target_dll)

    (DIST / 'Dados').mkdir(parents=True, exist_ok=True)
    (DIST / 'logs').mkdir(parents=True, exist_ok=True)

    # Copy runtime configuration and database.
    if (ROOT / 'local_params.txt').exists():
        shutil.copy2(ROOT / 'local_params.txt', DIST / 'local_params.txt')

    db_file = ROOT / 'Dados' / 'DADOS.DB'
    if db_file.exists():
        shutil.copy2(db_file, DIST / 'Dados' / 'DADOS.DB')

    return DIST


if __name__ == '__main__':
    ensure_runtime_structure()
    print('Runtime preparado em:', DIST)
