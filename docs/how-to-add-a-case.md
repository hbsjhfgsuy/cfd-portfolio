# 怎么把一个算例提交进仓库

算例做完后，**不要把工程文件整体拷进来**。Fluent 的 .cas / .dat 动辄几百 MB，
进 git 会把仓库撑爆——而且它们对看仓库的人毫无价值（他打不开，也不需要）。

要提交的是"证据"，不是"工程"。

## 1. 每个算例提交这五类文件

| 类型 | 放哪 | 是否入库 | 说明 |
|------|------|----------|------|
| 设置摘要 | setup.md 或 README 里的表格 | ✅ 必须 | 边界条件、模型、离散格式、收敛判据。这是别人拿到手最想看的一页 |
| 对标数据 | data/*.csv | ✅ 必须 | 从 Fluent 导出的 ASCII 曲线（File → Export → ASCII），几十 KB |
| 图 | figures/*.png | ✅ 必须 | CFD-Post 直接导出 PNG，单张控制在 300 KB 内 |
| 报告 | report.pdf | ✅ 可选 | 导出 PDF 且 < 10 MB 才放；超了就只放图和 md |
| 工程文件 | case/*.cas, *.dat | ❌ 绝不 | 已在 .gitignore 里，git 会自动忽略 |

## 2. 目录模板

```text
projects/0X-项目名/算例名/
├─ README.md        算例说明 + 对标结果（主体）
├─ setup.md         求解器设置表
├─ data/            导出的 CSV（自算结果 + 参考数据）
├─ figures/         对标图、云图、残差图
└─ case/            工程文件（.gitignore 已忽略，可以不建）
```

## 3. 三条命令

```bash
cd C:/Users/Administrator/Desktop/CFD/cfd-portfolio
git status                 # 看一眼都改了什么，别把 200 MB 的 .dat 带进来
git add -A
git commit -m "feat(01a): 圆管层流三套网格，压降误差 0.6%"
git push
```

现在 push 不会再问密码（SSH 已配好）。

## 4. 提交信息的写法

格式：类型(项目编号)：做了什么 + 关键数字

| 类型 | 用在哪 |
|------|--------|
| feat | 新算例、新结果 |
| fix | 网格/模型设置修正（改完重算） |
| docs | 只改文字、补图 |
| chore | 脚本、依赖、结构整理 |

例子：
- feat(01b): 后台阶 SST 模型再附着长度误差 6.8%
- fix(02): 值班火焰边界温度从 1800 K 改为 1880 K 后重算
- docs(02): 补充辐射对轴向温度影响的讨论

## 5. 提交前检查

- 单文件是否超过 10 MB？（GitHub 单文件硬上限 100 MB，超过就无法推送）
- data/ 里是不是二进制或者超长表格？（.Yall 那种 12 万行的单发数据不要放，先做统计）
- 图里有中文乱码吗？（matplotlib 默认字体不显示中文，要么装字体配 rcParams，要么图内用英文）
- README 里的数字和图表对得上吗？（别人会照着数字追问）

## 6. 不想每条命令都敲？

Windows 下可以建个快捷方式，或者把下面这行存成 push.ps1 放在仓库根目录：

```powershell
git add -A; git commit -m "update"; git push
```

但**不建议**长期用这种"一键提交"——提交信息是给别人（和三个月后的你）看的，
写清楚做了什么，比省那 10 秒值钱。
