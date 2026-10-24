"""把 Fluent 导出的径向剖面与解析解对比，出图并打印误差表。

用法
----
1. 在 Fluent 里导出剖面（File -> Export -> Solution Data -> ASCII），存成：
       data/profile_coarse.csv
       data/profile_medium.csv
       data/profile_fine.csv
   导出列至少要有：径向坐标(r 或 y) 和 轴向速度。
   2D 轴对称且对称轴放在 y=0 时，直接用 y 作为 r。

2. 跑：
       python scripts/compare.py

输出：figures/profile_comparison.png + 终端里的误差表（可直接贴进 README）
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

R = 0.005      # 半径 [m]，与 analytical.py 保持一致
U_MEAN = 0.1   # 体均速度 [m/s]

plt.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 200, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.3, "axes.linewidth": 0.8,
})


def read_fluent_ascii(path: Path):
    """读 Fluent 导出的 ASCII 表，返回 (表头, 数值行)。兼容引号表头和空行。"""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    header = []
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        tokens = stripped.split()
        values = []
        ok = len(tokens) >= 2
        if ok:
            for tok in tokens:
                try:
                    values.append(float(tok))
                except ValueError:
                    ok = False
                    break
        if ok:
            rows.append(values)
        elif not rows:
            header = [t.strip('"').strip() for t in tokens]
    return header, rows


def pick_columns(header, rows):
    """在表头里找径向坐标列和速度列；找不到就按 x, y, u 的位置猜。"""
    def find(keys, default):
        for i, name in enumerate(header):
            low = name.lower()
            if any(k in low for k in keys):
                return i
        return default

    i_r = find(["radial", "r-coordinate", "y-coordinate", "y"], 1)
    i_u = find(["axial velocity", "velocity"], 2 if len(rows[0]) > 2 else 1)
    if max(i_r, i_u) >= len(rows[0]):
        i_r, i_u = 1, 2
    return i_r, i_u


def u_analytical(r: float) -> float:
    ratio = min(max(r / R, 0.0), 1.0)
    return 2.0 * U_MEAN * (1.0 - ratio ** 2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data")
    parser.add_argument("--out", default="figures")
    args = parser.parse_args(argv)

    data_dir = Path(args.data)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in data_dir.glob("profile_*.csv") if "analytical" not in p.name)
    if not files:
        print(f"没有找到剖面文件。请把 Fluent 导出的 CSV 放到 {data_dir}/profile_*.csv")
        return 1

    styles = [("#1f77b4", "o"), ("#2ca02c", "s"), ("#d62728", "^"), ("#9467bd", "d")]

    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    grid = [i / 200.0 for i in range(201)]
    ax.plot([2 * (1 - g ** 2) for g in grid], grid, "-", color="k", lw=1.4,
            label="Analytical  2(1-(r/R)^2)")

    print("=" * 66)
    print("径向速度剖面对比（u/U_mean）")
    print("=" * 66)
    print(f"{'算例':<22}{'点数':>6}{'最大偏差':>12}{'相对 L2':>12}")
    print("-" * 66)

    worst = 0.0
    for path, (color, marker) in zip(files, styles):
        header, rows = read_fluent_ascii(path)
        i_r, i_u = pick_columns(header, rows)
        pts = sorted(((row[i_r], row[i_u]) for row in rows if abs(row[i_r]) <= R * 1.0001))
        if not pts:
            print(f"{path.stem:<22} 跳过（无 r<=R 的数据，检查坐标单位）")
            continue
        xs = [r / R for r, _ in pts]
        ys = [u / U_MEAN for _, u in pts]
        ax.plot(ys, xs, marker, ms=3.5, lw=1.0, color=color, label=path.stem.replace("profile_", "sim "))

        errs = [abs(u / U_MEAN - u_analytical(r) / U_MEAN) for r, u in pts]
        max_err = max(errs)
        l2 = math.sqrt(sum(e ** 2 for e in errs) / len(errs))
        worst = max(worst, max_err)
        print(f"{path.stem:<22}{len(pts):>6}{max_err*100:>11.2f}%{l2*100:>11.2f}%")

    ax.set_xlabel("u / U_mean [-]")
    ax.set_ylabel("r / R [-]")
    ax.set_xlim(0, 2.2)
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, fontsize=7.5, loc="center right")
    ax.set_title("Laminar pipe flow: velocity profile vs analytical", fontsize=10)
    fig.tight_layout()
    target = out_dir / "profile_comparison.png"
    fig.savefig(target)
    plt.close(fig)
    print("-" * 66)
    print(f"最大偏差 {worst*100:.2f}%   ->  {'通过 (<1%)' if worst < 0.01 else '未通过，检查网格与边界'}")
    print(f"图已写出: {target}")

    # ---- 网格无关性（可选）----
    mesh_csv = data_dir / "mesh_study.csv"
    if mesh_csv.exists():
        with mesh_csv.open(encoding="utf-8") as fh:
            records = [r for r in csv.DictReader(x for x in fh if not x.startswith("#"))]
        if records:
            names = [r["mesh"] for r in records]
            cells = [float(r["cells"]) for r in records]
            dps = [float(r["dp"]) for r in records]
            fig2, ax2 = plt.subplots(figsize=(4.4, 3.2))
            ax2.plot(cells, dps, "-o", color="#c0392b", ms=5)
            for n, c, d in zip(names, cells, dps):
                ax2.annotate(n, (c, d), textcoords="offset points", xytext=(6, 4), fontsize=7)
            ax2.set_xscale("log")
            ax2.margins(x=0.18)
            ax2.set_xlabel("cells [-]")
            ax2.set_ylabel("pressure drop [Pa]")
            ax2.set_title("Mesh independence: pressure drop", fontsize=9)
            fig2.tight_layout()
            fig2.savefig(out_dir / "mesh_study.png")
            plt.close(fig2)

            print()
            print("=" * 66)
            print("网格无关性")
            print("=" * 66)
            print(f"{'网格':<14}{'单元数':>10}{'压降[Pa]':>12}{'相对最密网格':>14}")
            ref = dps[-1]
            for n, c, d in zip(names, cells, dps):
                print(f"{n:<14}{c:>10.0f}{d:>12.3f}{(d-ref)/ref*100:>13.2f}%")
            print(f"\n图已写出: {out_dir / 'mesh_study.png'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
