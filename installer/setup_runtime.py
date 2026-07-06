import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist' / 'SOFME'


def ensure_runtime_structure():
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / 'Dados').mkdir(parents=True, exist_ok=True)
    (DIST / 'logs').mkdir(parents=True, exist_ok=True)
    (DIST / 'assets').mkdir(parents=True, exist_ok=True)

    # Copy source assets
    assets_src = ROOT / 'app' / 'images'
    if assets_src.exists():
        shutil.copytree(assets_src, DIST / 'assets' / 'images', dirs_exist_ok=True)

    # Copy local params template
    if (ROOT / 'local_params.txt').exists():
        shutil.copy2(ROOT / 'local_params.txt', DIST / 'local_params.txt')

    # Copy database folder if it exists
    db_src = ROOT / 'Gestão de Produção' / 'Dados'
    if db_src.exists():
        shutil.copytree(db_src, DIST / 'Dados', dirs_exist_ok=True)

    return DIST


if __name__ == '__main__':
    ensure_runtime_structure()
    print('Runtime preparado em:', DIST)
