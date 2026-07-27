#!/usr/bin/env python3
"""アクション提案の再実行前に、古い提案だけを削除する。"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_DIR = ROOT / ".analysis" / "current"
REPORTS_DIR = ROOT / "reports"

STALE_PATHS = {"actions": (REPORTS_DIR / "actions.md",)}


def prepare_stage(stage: str, current_dir: Path = CURRENT_DIR) -> list[Path]:
    expected_parent = ROOT / ".analysis"
    if current_dir.parent != expected_parent or current_dir.name != "current":
        raise RuntimeError(f"unsafe current directory: {current_dir}")
    if not current_dir.is_dir():
        raise FileNotFoundError(
            ".analysis/current/ がありません。先に分析段階を実行してください。"
        )

    removed: list[Path] = []
    for target in STALE_PATHS[stage]:
        allowed = target.parent == REPORTS_DIR
        if not allowed:
            raise RuntimeError(f"unsafe stale path: {target}")
        if target.exists():
            target.unlink()
            removed.append(target)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an analysis phase")
    parser.add_argument("stage", choices=sorted(STALE_PATHS))
    args = parser.parse_args()
    removed = prepare_stage(args.stage)
    print(f"stage {args.stage}: removed {len(removed)} stale outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
