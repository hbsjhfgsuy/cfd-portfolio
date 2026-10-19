# data/ —— 数据来源与使用说明

## 来源

**TNF Workshop**（International Workshop on Measurement and Computation of Turbulent Flames）
页面：<https://tnfworkshop.org/data-archives/pilotedjet/ch4-air/>

- **无需注册、无需登录**，数据为公开直链，可直接用浏览器或脚本下载。
- 数据版本：*Sandia/TUD Piloted CH4/Air Jet Flames, Data Release 2.0, January 2003*（含火焰 C、D、E、F 的标量数据）。

| 文件 | 大小 | 内容 |
|------|------|------|
| SandiaPilotDoc21.pdf | 200 KB | 实验文档：构型、边界条件、不确定度 |
| pmCDEF.zip | 7.9 MB | 火焰 C/D/E/F 标量数据（Raman/Rayleigh/LIF），含单发与系综平均 |
| LongRecordsFlameD.zip | 3.5 MB | Flame D 长序列单点数据（统计量、PDF 用） |
| TUD_LDV_DEF.zip | 28 KB | TU Darmstadt LDV 速度数据（火焰 D/E/F） |

`raw/` 目录不纳入 git（见根目录 .gitignore），用脚本重新生成即可：

```bash
python scripts/fetch_flameD.py --extract
```

`processed/` 目录是整理后的 CSV，**会**提交进仓库——任何人点开就能看，不需要装任何东西。

## 解压后的目录

```text
raw/
├─ pmCDEF/pmCDEFarchives/
│  ├─ pmD.stat/    系综平均剖面：D01 D02 D03 D075 D15 D30 D45 D60 D75 DCL
│  │               （每个站点有 .Yave / .Yfav / .Ycnd 三个版本）
│  └─ pmD.scat/    单发（single-shot）数据：D075 D15 D30 D45 D60 D75 的 .Yall
├─ LongRecordsFlameD/
│  └─ Long point data/   D15r00 ... D45r27 共 18 个长序列文件
└─ TUD_LDV_DEF/
   └─ TUD_LDV_D.axial, TUD_LDV_D.d01 ... .d60, .exit
```

## 文件格式

### 标量数据（.Yave / .Yfav / .Yall）

前 4 行是文本头，第 4 行是列名；之后是空白分隔的数值表：

```text
File: D15.Yave
Sandia piloted CH4-air jet flame D (1997)
Profile of ensemble average mass fractions
   r/d    F       Frms    T(K)   Trms   YO2 ...
  -0.56  0.7658  0.1093   907.   309.  1.29E-01 ...
```

- `.Yave` = 系综（Reynolds）平均
- `.Yfav` = Favre（密度加权）平均
- `.Ycnd` = 条件平均
- 列含义：r/d 半径、F 混合分数、T 温度[K]、Y* 组分质量分数，`*rms` 为脉动均方根

### 速度数据（TUD_LDV_*）

以 `#` 开头的元数据行 + 数据表，解析逻辑见 `scripts/flamed_io.py`。

## 踩过的坑（照抄会出错）

1. **`DCL.Yave` 表头写的是 r/d，但第一列实际是 x/d**（数值 5, 10, 15 … 80）。
   本仓库解析器用 `coord="x/d"` 强制改正；自己手写脚本时务必注意。
2. **文件名省略小数点**：`D075` = x/d 7.5，`D75` = x/d 75。两者在同一目录中并存，按字符正则容易撞车。
3. **列名有重复**：`YCOrms` 出现两次（第二个来自 CO-LIF 测量），解析器会自动改名为 `YCOrms_2`。
4. **剖面只覆盖部分半径**，不是完整的 −3d 到 +3d；画图时不要假设对称后自行镜像。
5. 单发数据（`.Yall`）行数很大（每个文件约 12 万行），画图时先做统计再绘，别直接 scatter。

## 引用

使用这些数据请引用原始文献：

- Barlow, R. S. and Frank, J. H., *Proc. Combust. Inst.* **27**:1087–1095 (1998).
- Barlow, R. S., Frank, J. H., Karpetis, A. N., Chen, J.-Y., *Combust. Flame* **143**:433–449 (2005).
- Schneider, Ch., Dreizler, A., Janicka, J., *Combust. Flame* **135**:185–190 (2003).

## 许可

实验数据版权归原始测量者（Sandia National Laboratories / TU Darmstadt）；
TNF Workshop 已将其公开供燃烧模型验证使用，本站仅做格式整理与再分发。
商用前请自行确认授权，并务必引用上述文献。
