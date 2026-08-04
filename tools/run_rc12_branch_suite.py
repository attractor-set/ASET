from __future__ import annotations

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
FROZEN_ROOT = REPOSITORY / "seed/releases/0.1-rc11/expanded"
SOURCE = FROZEN_ROOT / "tests/run_branch_suite.py"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    old = '''ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "machine" / "reference"))
import seed_reference as sut
'''
    new = f'''ROOT = Path({str(FROZEN_ROOT)!r})
sys.path.insert(0, {str(REPOSITORY / "src")!r})
from aset_seed import core as sut
'''
    if old not in source:
        print("RC12_BRANCH_SUITE_ERROR=upstream harness import block changed")
        return 1
    patched = source.replace(old, new, 1)
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    try:
        exec(compile(patched, str(SOURCE), "exec"), namespace, namespace)
    except SystemExit as error:
        return int(error.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
