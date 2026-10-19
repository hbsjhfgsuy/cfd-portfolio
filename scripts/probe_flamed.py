"""体检脚本：核对数据是否下载完整，并打印 Flame D 的工况与可用剖面。

    python scripts/probe_flamed.py
    python scripts/probe_flamed.py --raw data/raw
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flamed_io import parse_station, read_profile  # noqa: E402

EXPECTED = {
    "SandiaPilotDoc21.pdf": 150_000,
    "pmCDEF.zip": 6_000_000,
    "LongRecordsFlameD.zip": 2_500_000,
    "TUD_LDV_DEF.zip": 20_000,
}


def check_archives(raw: Path) -> bool:
    print("=" * 62)
    print("1. 存档完整性")
    print("=" * 62)
    ok = True
    for name, floor in EXPECTED.items():
        path = raw / name
        if not path.exists():
            print(f"  [缺失] {name}")
            ok = False
            continue
        size = path.stat().st_size
        flag = "OK" if size >= floor else "偏小"
        print(f"  [{flag:>4}] {name:<24} {size:>10,} B")
        ok = ok and size >= floor
    return ok


def check_profiles(raw: Path) -> bool:
    print()
    print("=" * 62)
    print("2. Flame D 标量剖面（系综平均）")
    print("=" * 62)

    stat_dir = raw / "pmCDEF" / "pmCDEFarchives" / "pmD.stat"
    if not stat_dir.is_dir():
        print(f"  [缺失] {stat_dir} —— 请先运行 fetch_flameD.py --extract")
        return False

    files = sorted(p.name for p in stat_dir.glob("*.Yave"))
    print(f"  目录: {stat_dir}")
    print(f"  文件: {len(files)} 个  ({', '.join(files[:6])} ...)")
    print()

    probe = stat_dir / "D15.Yave"
    columns, rows = read_profile(probe)
    print(f"  示例 {probe.name}: {len(rows)} 个径向点, {len(columns)} 列")
    print(f"  列名: {', '.join(columns[:10])} ...")
    stations = sorted(
        (parse_station(f)[1] for f in files if parse_station(f)[1] is not None)
    )
    print(f"  径向剖面位置 x/d: {stations}")

    cl = stat_dir / "DCL.Yave"
    if cl.exists():
        cols, data = read_profile(cl, coord="x/d")
        print(f"  中心线 DCL.Yave: {len(data)} 点, x/d 从 {data[0][0]:.1f} 到 {data[-1][0]:.1f}")
    return True


def show_conditions(raw: Path) -> None:
    print()
    print("=" * 62)
    print("3. 边界条件速查（建模时必须对齐）")
    print("=" * 62)
    ldv = raw / "TUD_LDV_DEF" / "TUD_LDV_D.axial"
    if not ldv.exists():
        print("  (未找到 LDV 数据)")
        return
    for line in ldv.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("#") and ("=" in line):
            text = line.strip().lstrip("#").strip()
            if any(k in text for k in ("diameter", "bulk", "Reynolds", "fuel", "pilot", "data")):
                print(f"  {text}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw")
    args = parser.parse_args(argv)

    raw = Path(args.raw)
    if not raw.is_absolute():
        raw = Path.cwd() / raw

    ok = check_archives(raw)
    if ok:
        ok = check_profiles(raw)
        show_conditions(raw)

    print()
    print("=" * 62)
    print("结论:", "数据齐备，可以开始建模。" if ok else "数据不完整，请检查上面的提示。")
    print("=" * 62)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
