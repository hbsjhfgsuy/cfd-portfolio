# Fluent 圆管层流 · GUI 全流程（2025 R2 / v252）

> **版本声明**：本文按你机器上的 Ansys 2025 R2 写的。Ansys 每年改界面，
> 标注 ⚠ 的地方是版本差异高发区，以你屏幕上的实际菜单为准。
> 标 ✅ 的是跨版本稳定的操作。

---

## 0. 先修正计划里的一个说法

你计划里写"官方教程在安装目录 help/ 下"。**这条对 2025 R2 不成立了。**

实测你这台机器：

```text
D:\Program Files\ANSYS Inc\v252\fluent\  下没有 tutorial 目录
全盘 ANSYS 目录里 .msh / .cas 教程文件数量 = 0
```

新版把 Fluent Tutorial Guide 的案例文件移到了在线（help.ansys.com / Learning Hub），
本地只装求解器。所以 W43 找 mixing elbow 案例时，别在安装目录里翻。

替代来源见第 6 节。

---

## 1. 路线选择：本算例用 Workbench + Meshing

| 路线 | 适合 | 本算例 |
|------|------|--------|
| Workbench + **Meshing**（结构四边形） | 2D 简单几何 | ✅ **推荐**，5 分钟出网格 |
| Workbench + **Fluent Meshing**（watertight） | 3D 复杂几何，企业主流 | 留到 W43 mixing elbow 再练 |

理由：矩形域的四边形网格用 Meshing 的 Mapped Face 比 watertight 快得多，
这个算例的目的是验证流程，不是练网格技术。

---

## 2. 几何（Workbench → SpaceClaim）

> 更详细的 2D 画法与网格操作见 [2d-modeling-meshing.md](2d-modeling-meshing.md)。

✅ **2.1 建系统**

Workbench 左侧 Toolbox → Component Systems → 把 **Fluid Flow (Fluent)** 拖进 Project Schematic。

⚠ **2.2 设成 2D**

在 Project Schematic 里点 Geometry 单元格 → 左侧 Properties 面板 → **Analysis Type** 改成 **2D**。
这一步漏了后面全是 3D，改起来很麻烦。

⚠ **2.3 画矩形**

双击 Geometry → SpaceClaim →
- 选 **XY 平面**作草图平面
- 进 **Sketch** 模式，用 **Rectangle** 工具从 (0, 0) 拖到 (1.2, 0.005)
- 画完在 Sketch 的 **Dimensions** 里改成精确值
- 退出草图 → 得到一个**面（surface）**，不是实体

✅ **2.4 命边界名**

SpaceClaim 左侧 **Groups** 面板 → Create Group → 选边 → 命名：

| 边 | 位置 | 名称 |
|----|------|------|
| 左 | x = 0 | inlet |
| 右 | x = 1.2 | outlet |
| 上 | y = 0.005 | wall |
| 下 | y = 0 | **axis** |

这些名字会传到 Meshing 变成边界条件，拼错要回来改。

---

## 3. 网格（Meshing）

⚠ **3.1** 双击 Mesh 打开 Meshing，确认顶部显示 **2D**。

⚠ **3.2 分段数**

2D 结构网格的常规做法：给四条边各加 **Number of Divisions**（Edge Sizing）：

| 网格 | 上/下边分段 | 左/右边分段 | 单元数 |
|------|-------------|-------------|--------|
| coarse | 240 | 30 | 7 200 |
| medium | 480 | 60 | 28 800 |
| fine | 960 | 120 | 115 200 |

⚠ **3.3 映射**

右键 Mesh → Insert → **Face Meshing** → 选该面，强制四边形结构化。

✅ **3.4 生成**

右键 Mesh → **Generate Mesh**。检查 Quality → **Orthogonal Quality**，结构四边形应 > 0.95。

✅ **3.5** 关掉 Meshing 回 Workbench，Mesh 单元格显示绿色对勾。

---

## 4. 求解设置（Fluent）

双击 **Setup** 打开 Fluent Launcher：
- ⚠ 勾 **2D**（几何设成 2D 后会自动勾上）
- 勾 **Double Precision**
- Start

### 4.1 General ✅

| 面板项 | 设置 |
|---|---|
| Solver | **Pressure-Based** |
| Time | **Steady** |
| 2D Space | **Axisymmetric** ← 关键 |

⚠ 这是唯一容易错的地方。默认是 Planar，算的是两块无限大平板之间的流动，
摩擦因子是 96/Re 而不是 64/Re，压降差 50%。

### 4.2 Models → Viscous ✅

选 **Laminar**。Re = 995，层流，不开湍流模型。

### 4.3 Materials ✅

Materials → Fluid → Create/Edit → Fluent Database → 选 **water-liquid** → Copy → Close。
确认 Density = 998.2，Viscosity = 0.001003。

### 4.4 Boundary Conditions ✅

| 边界 | 类型 | 设置 |
|------|------|------|
| inlet | velocity-inlet | Velocity Magnitude = **0.1 m/s** |
| outlet | pressure-outlet | Gauge Pressure = **0 Pa** |
| wall | wall | 默认 no-slip，静止 |
| axis | **axis** | 确认类型是 axis，不是 wall |

⚠ 如果 inlet 下拉里只有 wall / interface，说明 SpaceClaim 里 Groups 没命名成功，回 2.4。

### 4.5 Solution Methods ✅

| 项 | 设置 |
|---|---|
| Scheme | **SIMPLE** |
| Gradient | Least Squares Cell Based（默认） |
| Pressure | **Second Order** |
| Momentum | **Second Order Upwind** |

### 4.6 监控质量守恒 ✅

Reports → **Fluxes → Mass Flow Rate** → 勾 inlet 和 outlet → 勾 **Print to Console**。
这样每次迭代都打印进出口流量，守恒情况一眼看出。

### 4.7 初始化与迭代 ✅

- Initialization → **Standard** → Compute from **inlet** → Initialize
- Run Calculation → Number of Iterations = **500** → Calculate

层流通常 100–200 步残差掉到 1e-6。

---

## 5. 后处理（采集那四样东西）

### 5.1 径向速度剖面 ✅

1. Results → **Surface → Line/Rake**
2. 两个端点：**(1.0, 0)** 和 **(1.0, 0.005)**。2D 里坐标是 (x, y)，y 就是 r
3. New Surface Name 写 profile_x1p0 → Create
4. File → **Export → Solution Data → ASCII**
   - Surfaces 选 profile_x1p0
   - 只勾 **Axial Velocity**
   - 文件名 profile_medium.csv

⚠ 导出前确认 **Units 是 SI**，否则坐标变 mm，脚本读不到。

### 5.2 壁面压力沿程 ✅

Plot → XY Plot → 选 wall → 横轴 X，纵轴 **Static Pressure**。
形状：前 0.6 m 略弯（发展段），之后必须是直线。

### 5.3 中心线速度 ✅

- Line/Rake：从 (0, 0) 到 (1.2, 0)，命名 centerline
- 导出 Axial Velocity，画沿 x 的曲线
- 预期：x > 0.6 m 后稳定在 **0.2 m/s**

### 5.4 压降（关键）✅

**不要**用 inlet 和 outlet 的平均压力相减——那是总压降，含入口效应，会偏高 16%。

正确做法，取充分发展段：

1. Reports → **Surface Integrals → Area-Weighted Average → Static Pressure**
2. 分别对 x = 0.7 和 x = 1.2 两个位置（用 Plane 建面，或直接在 XY Plot 上读点）
3. 相减 → 理论值 **16.05 Pa**

---

## 6. 官方教程与案例去哪找

**本地已有**（2026-10-24 放入）：
C:\Users\Administrator\Desktop\CFD\VMFluent_2023R1 —— 1.04 GB，578 个文件，
包含 2023 R1 官方 V&V 案例库 VM01–VM70（每个含 .scdoc 几何、.msh、.cas.h5、.dat.h5、
.trn 操作日志、.xy/.csv 实验对标数据）和 MixingElbow 全套（含中文教程与成品 case）。

注意：这是 **2023 R1** 的案例库，不是 2025 R2 安装包自带的。用 2025 R2 打开会提示版本转换，
另存为新文件，别覆盖原件。

**2025 R2 安装目录里没有教程案例**（实测 fluent 目录下 .msh/.cas 数量为 0），新版已移到在线：

| 来源 | 内容 | 说明 |
|------|------|------|
| **help.ansys.com** | 官方 Fluent 文档，含 Tutorial Guide 全文 | 需注册 Ansys 账号（免费） |
| **Ansys Innovation Courses**（courses.ansys.com） | 免费视频课，Fluent 入门系列 | 注册即用，适合看操作动作 |
| **Ansys Learning Forum**（innovationspace.ansys.com/forum） | 官方 tutorial 输入文件（.msh/.cas） | 搜 tutorial input files |
| Cornell SimCafe | 经典分步图文教程（Workbench 流程） | 境外站，国内访问可能不稳 |

⚠ 我这边抓这几个站点时被挡（403 / 超时），没法替你验证当前可访问性。
你浏览器挂着代理应该能开；打不开告诉我，我换路径。

---

## 7. 三个自检（每次改完设置都跑一遍）

| 检查 | 方法 | 通过标准 |
|------|------|----------|
| 维度对不对 | General 面板看 2D Space | Axisymmetric |
| 守恒不守恒 | 控制台打印的进出口质量流率 | 差值 < 0.1% |
| 发展段到没到 | 中心线速度沿 x | x > 0.6 m 后 = 0.2 m/s |

三个都过，再去跑另外两套网格。
