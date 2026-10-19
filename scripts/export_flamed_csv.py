"""把 Flame D 的二进制/文本剖面导出为整洁的 CSV，便于 Excel / Origin / Python 复用。

    python scripts/export_flamed_csv.py

输出
----
data/processed/flamedD_centerline.csv   中心线 (x/d)
data/processed/flamedD_radial_xdXX.csv  各径向剖面 (r/d)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flamed_io import parse_station, read_profile, write_csv  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw")
    parser.add_argument("--out", default="data/processed")
    args = parser.parse_args(argv)

    raw = Path(args.raw)
    out = Path(args.out)
    stat = raw / "pmCDEF" / "pmCDEFarchives" / "pmD.stat"
    if not stat.is_dir():
        print(f"未找到 {stat}，请先运行 fetch_flameD.py --extract", file=sys.stderr)
        return 1

    source = "TNF Workshop, Sandia/TUD piloted CH4-air flames, Release 2.0 (2003)"

    count = 0
    for path in sorted(stat.glob("D*.Yave")):
        flame, station = parse_station(path.name)
        if flame != "D":
            continue
        is_cl = path.stem.upper() == "DCL"
        coord = "x/d" if is_cl else "r/d"
        columns, rows = read_profile(path, coord=coord)
        if is_cl:
            target = out / "flamedD_centerline.csv"
        else:
            # 7.5 -> 7p5，75 -> 75，避免 D075 与 D75 撞名
            tag = f"{station:g}".replace(".", "p")
            target = out / f"flamedD_radial_xd{tag}.csv"
        write_csv(
            columns,
            rows,
            target,
            meta={
                "source": source,
                "file": path.name,
                "profile": "ensemble average",
                "station_x_over_d": "centerline" if is_cl else station,
            },
        )
        count += 1
        print(f"  {path.name:<14} -> {target.relative_to(out.parent)}  ({len(rows)} rows)")

    print()
    print(f"共导出 {count} 个 CSV 到 {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
