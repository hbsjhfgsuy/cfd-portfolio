"""圆管层流（Poiseuille）解析解：生成参考剖面 CSV，并打印理论预期值。

    python scripts/analytical.py

为什么要先跑这个：算例开工前先把"正确答案"算出来写进报告，再去跑 Fluent。
否则很容易变成"算完看看数字像不像"，那不叫验证。

修改几何/工况只需要改下面的参数。
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

# ---- 工况参数（与 Fluent 设置必须一致）----
D = 0.010          # 管径 [m]
R = D / 2.0        # 半径 [m]
L = 1.2            # 管长 [m]
U_MEAN = 0.1       # 体均速度 [m/s]
RHO = 998.2        # 水的密度 [kg/m3]
MU = 0.001003      # 水的动力粘度 [Pa.s]
N_POINTS = 41      # 径向采样点数


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/analytical_profile.csv")
    args = parser.parse_args(argv)

    re = RHO * U_MEAN * D / MU
    f_darcy = 64.0 / re
    dp = f_darcy * (L / D) * (RHO * U_MEAN**2 / 2.0)
    q = U_MEAN * math.pi * D**2 / 4.0
    dp_hp = 128.0 * MU * L * q / (math.pi * D**4)
    u_max = 2.0 * U_MEAN
    tau_w = 8.0 * MU * U_MEAN / D
    l_entrance = 0.06 * re * D

    print("=" * 58)
    print("圆管层流 · 理论预期值")
    print("=" * 58)
    print(f"  管径 D              = {D*1000:.1f} mm")
    print(f"  管长 L              = {L:.2f} m   (L/D = {L/D:.0f})")
    print(f"  体均速度 U_mean     = {U_MEAN} m/s")
    print(f"  雷诺数 Re           = {re:.1f}   (层流判据 < 2300)")
    print(f"  入口段长度 Le       = {l_entrance:.3f} m  (~{l_entrance/D:.0f} D)")
    print()
    print(f"  中心线速度 u_max    = {u_max:.4f} m/s")
    print(f"  Darcy 摩擦因子 f    = {f_darcy:.5f}")
    print(f"  压降 (f·L/D·ρU²/2)  = {dp:.3f} Pa")
    print(f"  压降 (Hagen-Poiseuille) = {dp_hp:.3f} Pa   <- 两者应一致")
    print(f"  壁面剪应力 tau_w    = {tau_w:.5f} Pa")
    print()
    if L > l_entrance * 1.5:
        print(f"  OK: L={L} m 足够长，x > {l_entrance:.2f} m 后可视为充分发展")
    else:
        print(f"  WARNING: L 偏短，出口可能未充分发展，建议 L > {l_entrance*1.5:.2f} m")

    # 解析速度剖面 u(r) = 2*U_mean*[1-(r/R)^2]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# 圆管层流解析解 u(r)=2*U_mean*(1-(r/R)^2), D={D}, L={L}, U_mean={U_MEAN}\n")
        fh.write(f"# Re={re:.1f}, f={f_darcy:.5f}, dp_theory={dp:.3f} Pa\n")
        writer = csv.writer(fh)
        writer.writerow(["r", "r_over_R", "u", "u_over_Umean"])
        for i in range(N_POINTS):
            r = R * i / (N_POINTS - 1)
            u = u_max * (1.0 - (r / R) ** 2)
            writer.writerow([f"{r:.6e}", f"{r/R:.4f}", f"{u:.6e}", f"{u/U_MEAN:.4f}"])

    print(f"\n参考剖面已写出: {out}  ({N_POINTS} 点)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
