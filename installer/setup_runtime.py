import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist' / 'SOFME'
BUILD = ROOT / 'build' / 'SOFME'


def ensure_runtime_structure():
    if DIST.exists():
        shutil.rmtree(DIST)

    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / 'Dados').mkdir(parents=True, exist_ok=True)
    (DIST / 'logs').mkdir(parents=True, exist_ok=True)

    # Copy PyInstaller build output files needed at runtime.
    if (BUILD / 'SOFME.exe').exists():
        shutil.copy2(BUILD / 'SOFME.exe', DIST / 'SOFME.exe')
    if (BUILD / 'SOFME.pkg').exists():
        shutil.copy2(BUILD / 'SOFME.pkg', DIST / 'SOFME.pkg')
    if (BUILD / 'localpycs').exists():
        shutil.copytree(BUILD / 'localpycs', DIST / 'localpycs')

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
