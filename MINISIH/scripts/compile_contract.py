from __future__ import annotations

from pathlib import Path

from contracts.dao_treasury import compile_contract


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / 'artifacts'
OUTPUT_DIR.mkdir(exist_ok=True)


def main() -> None:
    approval_teal, clear_teal = compile_contract()
    (OUTPUT_DIR / 'dao_treasury.approval.teal').write_text(approval_teal, encoding='utf-8')
    (OUTPUT_DIR / 'dao_treasury.clear.teal').write_text(clear_teal, encoding='utf-8')
    print(f'Wrote TEAL to {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
