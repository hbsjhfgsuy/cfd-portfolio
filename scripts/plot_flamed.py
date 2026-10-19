"""绘制 Flame D 参考数据图：中心线温度与径向温度剖面。

    python scripts/plot_flamed.py

输出（可直接贴进报告 / README）
----
docs/figures/flamedD_centerline.png
docs/figures/flamedD_radial_T.png

这两张图的作用：把你的 Fluent/OpenFOAM 计算结果叠上去，就是标准的
"文献对标图"——报告里最有说服力的那种图。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flamed_io import parse_station, read_profile  # noqa: E402

plt.rcParams.update(
    {
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "font.size": 9,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.linewidth": 0.8,
    }
)

STATIONS = (15.0, 30.0, 45.0, 60.0)


def plot_centerline(stat: Path, out: Path) -> None:
    path = stat / "DCL.Yave"
    if not path.exists():
        print(f"跳过中心线：找不到 {path}")
        return
    columns, rows = read_profile(path, coord="x/d")
    i_x, i_t = columns.index("x/d"), columns.index("T")
    i_oh = columns.index("YOH") if "YOH" in columns else None

    x = [r[i_x] for r in rows]
    t = [r[i_t] for r in rows]

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(x, t, "-o", ms=3, lw=1.2, color="#c0392b", label="T (measured)")

    ax.set_xlabel("x/d [-]")
    ax.set_ylabel("Temperature [K]", color="#c0392b")
    ax.tick_params(axis="y", labelcolor="#c0392b")
    ax.set_xlim(0, max(x) * 1.05)
    ax.set_ylim(0, None)

    if i_oh is not None:
        yoh = [r[i_oh] for r in rows]
        ax2 = ax.twinx()
        ax2.plot(x, [v * 1e3 for v in yoh], "-s", ms=3, lw=1.0, color="#2471a3", label="YOH x1000")
        ax2.set_ylabel("Y(OH) x 1000 [-]", color="#2471a3")
        ax2.tick_params(axis="y", labelcolor="#2471a3")
        ax2.grid(False)

    ax.set_title("Sandia Flame D - centerline (ensemble average)", fontsize=10)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"  写出 {out}")


def plot_radial(stat: Path, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"]
    plotted = 0

    for station, color in zip(STATIONS, colors):
        candidates = list(stat.glob(f"D{int(station * 10):03d}.Yave"))
        if not candidates:
            candidates = list(stat.glob(f"D{int(station):02d}.Yave"))
        if not candidates:
            continue
        columns, rows = read_profile(candidates[0], coord="r/d")
        i_r, i_t = columns.index("r/d"), columns.index("T")
        r = [row[i_r] for row in rows]
        t = [row[i_t] for row in rows]
        ax.plot(r, t, "-o", ms=3, lw=1.1, color=color, label=f"x/d = {station:g}")
        plotted += 1

    if not plotted:
        print("跳过径向图：没有找到剖面文件")
        plt.close(fig)
        return

    ax.set_xlabel("r/d [-]")
    ax.set_ylabel("Temperature [K]")
    ax.set_xlim(-3, 3)
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Sandia Flame D - radial temperature profiles", fontsize=10)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"  写出 {out}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw")
    parser.add_argument("--out", default="docs/figures")
    args = parser.parse_args(argv)

    stat = Path(args.raw) / "pmCDEF" / "pmCDEFarchives" / "pmD.stat"
    if not stat.is_dir():
        print(f"未找到 {stat}，请先运行 fetch_flameD.py --extract", file=sys.stderr)
        return 1

    out = Path(args.out)
    plot_centerline(stat, out / "flamedD_centerline.png")
    plot_radial(stat, out / "flamedD_radial_T.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
