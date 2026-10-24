# 对标数据与文献清单

> 做仿真最贵的不是算力，是"算完了拿什么证明它对"。这份清单是本仓库所有项目的验证依据。
> 原则：**解析解 > 基准实验（有明确不确定度）> 他人已发表的仿真结果**。

## 1. 湍流燃烧基准数据

| 资源 | 内容 | 用途 | 地址 |
|------|------|------|------|
| **TNF Workshop** | Sandia Flame C/D/E/F、悉尼钝体火焰 HM1、旋流火焰的完整实验数据（温度、组分、速度） | 湍流燃烧模型验证的国际通用靶场 | <https://tnfworkshop.org> |
| Sandia Flame D 存档 | 本仓库 scripts/fetch_flameD.py 直接下载 | 非预混燃烧对标 | <https://tnfworkshop.org/data-archives/pilotedjet/ch4-air/> |

## 2. 化学动力学与机理

| 资源 | 内容 | 用途 | 地址 |
|------|------|------|------|
| GRI-Mech 3.0 | 天然气燃烧详细机理（53 组分 / 325 反应），Cantera 自带 gri30.yaml | 层流火焰速度、点火延迟计算 | <http://combustion.berkeley.edu/gri-mech/> |
| DRM22 | 甲烷骨架机理（22 组分），EDC 有限速率模型常用 | 降低 Fluent 燃烧计算量 | <http://combustion.berkeley.edu/drm/> |
| Cantera | 开源化学动力学工具，Python 接口 | 一维火焰、反应器、对冲火焰 | <https://cantera.org> |

## 3. 文献对标清单

| 物理问题 | 参考文献 | 用于 |
|----------|----------|------|
| 后台阶再附着 | Armaly, B. F. et al., *J. Fluid Mech.* **127**:473-496 (1983) | 层流/低 Re 再附着长度 |
| 后台阶再附着（高 Re） | Driver, D. M. & Seegmiller, H. L., *AIAA J.* **23**:163-171 (1985) | 湍流再附着，x/H 约为 6.3 |
| 层流火焰速度 | Gu, X. J. et al., *Combust. Flame* **121**:41-58 (2000) | CH4/空气当量比扫描 |
| 层流火焰速度 | Rozenchan, G. et al., *Proc. Combust. Inst.* **29**:1461-1469 (2002) | 高压/富燃侧 |
| 点火延迟 | Seery, D. J. & Bowman, C. T., *Combust. Flame* **14**:37-48 (1970) | 激波管数据 |
| Flame D 标量 | Barlow, R. S. & Frank, J. H., *Proc. Combust. Inst.* **27**:1087-1095 (1998) | 温度/组分剖面 |
| Flame D 标量与输运 | Barlow, R. S. et al., *Combust. Flame* **143**:433-449 (2005) | 完整标量结构与不确定度 |
| Flame D 速度 | Schneider, Ch. et al., *Combust. Flame* **135**:185-190 (2003) | LDV 速度剖面 |
| 钝体火焰 HM1 | Dally, B. B. et al., *Combust. Flame* **114**:119-134 (1998) | 钝体稳焰与局部熄火 |
| 家用燃烧器 | Boggavarapu, P. et al., *Fuel* **116** (2014) | 燃气灶热效率与排放 |

## 4. 工程标准

| 标准 | 内容 |
|------|------|
| GB 30720 | 家用燃气灶能效限定值，一级能效热效率不低于 63% |
| GB 16410-2020 | 家用燃气灶具，干烟气 CO 浓度不高于 0.05%，NOx 分级 |
