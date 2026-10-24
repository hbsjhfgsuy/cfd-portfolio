# 2D 几何与网格（Workbench → SpaceClaim → Meshing）

> 以圆管层流为例：矩形域 1.2 m × 0.005 m，2D 轴对称。
> 版本：Ansys 2025 R2。菜单名可能与你屏幕略有出入，但操作逻辑一致。

## 核心概念：2D 只画"一个面"

3D 建模产出的是**实体（solid）**，2D 建模产出的是**面（surface）**。
整个流程里最容易错的地方就在这里：如果你在 SpaceClaim 里 Pull 出了厚度，得到的就成了 3D 实体，
后面在 Meshing 里选 2D 会直接报错，或者生成的是一层薄片而不是平面。

判断标准：**Structure 树里应该只有一个 Surface，没有任何 Solid。**

---

## 步骤 1：Workbench 设成 2D

1. 打开 Workbench（开始菜单 → Ansys 2025 R2 → Workbench 2025 R2）
2. 左侧 Toolbox → **Component Systems** → 把 **Fluid Flow (Fluent)** 拖到右边的 Project Schematic
3. 点一下 **Geometry** 单元格（不是双击），看左边 **Properties** 面板
4. 找到 **Analysis Type**，从 3D 改成 **2D**
5. 双击 **Geometry**，选择在 **SpaceClaim** 中编辑

⚠ 第 4 步如果漏了，后面所有环节都是 3D，网格会变成"一层薄片"，改起来要重来。

---

## 步骤 2：SpaceClaim 画矩形面

### 2.1 先把单位改成米

File → **SpaceClaim Options** → Units → 长度单位选 **Meter**。
（默认常是 mm，不改的话待会儿输入 1.2 会变成 1.2 mm）

### 2.2 进入草图

1. 左侧 **Structure** 树里选 **XYPlane**
2. 视图左侧弹出的小工具栏里，点铅笔图标 **Sketch**，进入草图模式
3. 屏幕上方出现 Sketch 标签页

### 2.3 画矩形

1. Sketch 标签 → **Rectangle** 工具
2. 在网格上随便拖一个矩形（尺寸不准没关系）
3. 双击矩形的任一条边上的尺寸标注，改成精确值：
   - 长边 = **1.2**（沿 X）
   - 短边 = **0.005**（沿 Y）
4. 矩形左下角要**对齐原点**：用 **Sketch → Dimensions** 或直接把左下角拖到坐标原点，
   再用尺寸约束把它锁在 (0, 0)

### 2.4 退出草图得到面

点 **Sketch → Exit Sketch**（或按 Esc 两次）。

此时 Structure 树里应该出现 **1 个 Surface**，Shape 面板显示面积约 0.006 m²。
如果出现的是 Solid，说明不小心用了 Pull——删掉重来。

### 2.5 给四条边命名（可选）

左侧 **Groups** 面板 → **Create Group** → 选一条边 → 命名：

| 边 | 位置 | 名称 |
|----|------|------|
| 左 | x = 0 | inlet |
| 右 | x = 1.2 | outlet |
| 上 | y = 0.005 | wall |
| 下 | y = 0 | axis |

⚠ 这一步在某些版本里传不到 Meshing。**如果传丢了不用纠结，第 4 步在 Meshing 里重新命名更可靠。**

### 2.6 返回 Workbench

Ctrl+S 保存 → 关掉 SpaceClaim → Workbench 里 Geometry 单元格变绿勾。

---

## 步骤 3：Meshing 生成四边形网格

双击 **Mesh** 单元格 → 打开 Ansys Meshing。

### 3.1 确认是 2D

看模型树顶部或工具栏，应该显示 **2D**。如果显示 3D，回步骤 1 检查 Analysis Type。

### 3.2 加四条边的分段数

1. 右键 **Mesh** → Insert → **Sizing**
2. 选几何：点工具栏的**边选择**模式，框选**上下两条长边**（或用 Ctrl 逐条点）
3. Details 面板：
   - Type = **Number of Divisions**
   - Number of Divisions = **240**
4. 重复一次，选**左右两条短边**，Number of Divisions = **30**

| 网格 | 长边分段 | 短边分段 | 单元数 |
|------|----------|----------|--------|
| coarse | 240 | 30 | 7 200 |
| medium | 480 | 60 | 28 800 |
| fine | 960 | 120 | 115 200 |

### 3.3 强制四边形

右键 **Mesh** → Insert → **Face Meshing** → 选中那个面。
Details 里 Method 保持 **Quadrilateral**。

⚠ 不加 Face Meshing，Meshing 可能生成三角形网格，单元数会翻倍且不是结构网格。

### 3.4 生成

右键 **Mesh** → **Generate Mesh**。

生成完在模型树点 **Mesh** → Details → **Statistics**，看：
- Nodes / Elements 数量
- 应该是 **7200 个单元**（240 × 30）

### 3.5 检查质量

模型树 → **Mesh** → Details → **Quality** → Mesh Metric 选 **Orthogonal Quality**。
结构四边形应该 **> 0.95**，接近 1。

---

## 步骤 4：命名边界（Named Selections）

这是最关键的一步，Fluent 靠它识别边界。

1. 右键模型树里的 **Model**（或 Mesh） → **Insert → Named Selection**
2. 在工具栏切到**边选择**模式，点中一条边（按住 Ctrl 可多选）
3. Details 面板 → **Named Selection** 填名字
4. 重复四次：

| 名称 | 选哪条边 | 类型（Meshing 里不用设，Fluent 里改） |
|------|----------|--------------------------------------|
| inlet | 左（x=0） | velocity-inlet |
| outlet | 右（x=1.2） | pressure-outlet |
| wall | 上（y=0.005） | wall |
| axis | 下（y=0） | **axis**（Fluent 里改） |

⚠ 如果步骤 2.5 的 Groups 已经传过来了，这里会看到同名条目，确认四条都在即可，不用重复建。

---

## 步骤 5：进 Fluent 前最后检查

| 检查项 | 应在哪里看 | 通过标准 |
|--------|-----------|----------|
| 维度 | Meshing 工具栏 / Fluent Launcher | 2D |
| 单元数 | Mesh → Statistics | 约 7200 |
| 单元形状 | 视图里看 | 全是四边形，横平竖直 |
| 边界数 | 模型树 Named Selections | 正好 4 个 |
| 质量 | Quality → Orthogonal Quality | > 0.95 |

五项都过，关掉 Meshing，双击 **Setup** 打开 Fluent。

---

## 2D 特有的三个坑

### 坑 1：画成了实体

SpaceClaim 里如果用了 **Pull** 工具，会把面拉成有厚度的实体。
2D 算例只需要面。症状：Meshing 里选 2D 后报 "no valid geometry"，或生成的网格单元数远超预期。

### 坑 2：axis 边界没改成 axis 类型

网格里的边默认都是 wall。进 Fluent 后：
Boundary Conditions → 双击 **axis** → Type 下拉改成 **axis** → 确认。

⚠ 不改的话，那条边是壁面，等于算了一个封闭的半管，完全没流量。

### 坑 3：单位

SpaceClaim 用 mm，Fluent 里读进来就是 mm 尺度。1.2 m 的管子会变成 1.2 mm，Re 直接差 1000 倍。
进 Fluent 后 General → **Scale**，确认 Domain Extents 的 X 范围是 0–1.2，不是 0–1200。

---

## 附：不想用 SpaceClaim 的替代路线

直接开 **Fluent Meshing**（开始菜单里的 Fluent 2025 R2 → Fluent Meshing），用 watertight 工作流，
导入 .scdoc 后选 2D。这条路线和你 W43 要练的 mixing elbow 是同一套，学一次两处都能用。
但对这个矩形来说，Workbench + Meshing 更快。
