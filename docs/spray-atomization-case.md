# 气动雾化近场算例（air-blast atomizer）

> 来源：ANSYS Fluent Tutorial Guide 第 17 章 **Modeling Evaporating Liquid Spray**。
> 这个教程从 Fluent 12 就有，2025 R2 仍然保留，是官方唯一一个用 air-blast atomizer 的完整算例。

## 1. 算例是什么

一个**气动雾化喷嘴**（甲醇）向圆柱腔内喷射，伴随蒸发。几何取 **30° 扇区**
（1/12 圆周，两侧用周期性边界），这样能用少量网格代表整个轴对称喷注。

| 边界 | 类型 | 关键参数 |
|------|------|----------|
| central_air | mass-flow-inlet | 9.167e-5 kg/s，水力直径 0.0037 m，293 K |
| swirling_air | velocity-inlet | 19 m/s，**切向与轴向分量各 0.7071**（45° 旋流），水力直径 0.0043 m |
| co-flow-air | velocity-inlet | 1 m/s，水力直径 0.0726 m（伴流空气） |
| outer-wall | wall | Specified Shear |
| outlet | pressure-outlet | Backflow Direction: From Neighboring Cell |
| 两侧 | periodic | 30° 旋转周期 |

材料：甲醇 + 空气（组分输运，含甲醇蒸气；教程里删掉了 CO2 和 H2O）。

## 2. DPM 设置（教程原文）

| 项 | 值 |
|---|---|
| 模型 | Discrete Phase，**勾 Interaction with Continuous Phase** |
| 物理模型 | Droplet Collision + **Droplet Breakup (TAB)** |
| 破碎常数 | y0 = 0，Breakup Parcels = 2 |
| 阻力律 | **dynamic-drag**（只有开了破碎模型才可选） |
| 颗粒处理 | **Unsteady Particle Tracking**，Particle Time Step = 1e-4 s |
| 每 DPM 迭代的连续相迭代数 | 10 |
| 注入类型 | **air-blast-atomizer** |
| Particle Type | Droplet |
| 材料 | methyl-alcohol-liquid |
| 注入点 | (0, 0, 0.0015) m |
| 温度 | 263 K |
| 流量 | **8.5e-5 kg/s**（30° 扇区；整周要 ×12） |
| 颗粒流数 | 60 |

⚠ 教程强调：**先不开液滴算 300 步单相流场**，收敛后再注入。这和我前面说的顺序一致。

## 3. 两条实施路线

### 路线 A：忠实复现（3D 30° 扇区）

优点：和教程一一对应，参数照抄即可。
缺点：要建**周期性边界**的扇区网格，两天比较紧张；周期边界设错会直接算不出旋流。

### 路线 B：2D 轴对称 + 旋流（推荐先试）

这个算例本质是轴对称的，30° 扇区只是为了省网格。所以可以用：
**2D Axisymmetric Swirl**（General → 2D Space 选 Axisymmetric Swirl），
swirling_air 入口直接给**切向速度**，不需要周期性边界。

⚠ 不确定点：air-blast atomizer 注入模型在 2D 下是否可用，我没法在不启动 Fluent 的情况下验证。
如果 Injection Type 下拉里找不到它，就退回 **cone + Rosin-Rammler** 给分布。

## 4. 两天排期

| 时间 | 事 |
|---|---|
| 第 1 天上午 | 几何（轴对称：中心气道 + 环形液缝 + 旋流环 + 外筒）+ 网格 |
| 第 1 天下午 | 单相流场收敛（300 步量级），检查旋流是否有回流区 |
| 第 1 天傍晚 | 开 DPM，air-blast 注入，单向耦合跑通 |
| 第 2 天上午 | 开蒸发 + 双向耦合，看喷雾锥形与液滴存活 |
| 第 2 天下午 | 提取 SMD 沿程 + 粒径分布直方图，出图 |

## 5. 要交付的三个数（解耦接口）

1. **SMD / D32 沿轴向的曲线**：喷嘴出口到下游 100 mm，每 10 mm 一个截面
2. **某截面的粒径分布**：体积分数 vs 粒径分档（这才是管式炉的入口条件）
3. **喷雾锥角**

提取方法：Results → Reports → **Discrete Phase → SMD / DPM Concentration**，
按截面（Plane）或按边界统计；分布用 **Sample** 功能导出颗粒数据到文件，再用 Python 分档。

## 6. 参考链接

- 教程全文（HTML 镜像，Fluent 12）：<https://www.afs.enea.it/project/neptunius/docs/fluent/html/tg/node280.htm>
- air-blast 模型理论（2025 R2 帮助）：<https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_atomizer_air_blast.html>
- 中文资料：<https://atomgit.com/Open-source-documentation-tutorial/cf405>

2025 R2 的教程案例文件不在本地安装包里，需要去 help.ansys.com 下载 "Fluent Tutorial Files"。
