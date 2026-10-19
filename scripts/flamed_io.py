"""TNF Workshop 火焰数据读取器（纯标准库，无第三方依赖）。

支持两类文件
------------
1. Sandia/TUD 标量数据（pmCDEF.zip 解压后的 *.Yave / *.Yfav / *.Yall）
   格式：前 4 行为文本头，第 4 行为列名；其后为空白分隔的数值表。

2. TU Darmstadt LDV 速度数据（TUD_LDV_DEF.zip 解压后的 *.axial / TUD_LDV_D.dXX）
   格式：以 # 开头的元数据行，最后一行为列名。

用法
----
    from flamed_io import read_profile
    cols, rows = read_profile("data/raw/pmCDEF/pmCDEFarchives/pmD.stat/D15.Yave")
    df = read_profile_df(path)   # 需要 pandas

注意（实测踩到的坑）
-------------------
DCL.Yave（中心线文件）的表头写的是 r/d，但第一列实际是 x/d
（数值 5.00, 10.00, 15.00 ...）。绘图/对标时务必按 x/d 处理。
"""

from __future__ import annotations

import csv
from pathlib import Path

__all__ = ["read_profile", "read_profile_df", "write_csv", "parse_station"]


def _to_float(token: str) -> float:
    """兼容 Fortran 风格指数 1.0D+00。"""
    return float(token.replace("D", "E").replace("d", "e"))


def _is_numeric_row(tokens: list[str]) -> bool:
    if len(tokens) < 2:
        return False
    try:
        for tok in tokens:
            _to_float(tok)
    except ValueError:
        return False
    return True


def _dedup(names: list[str]) -> list[str]:
    """列名去重：重复列追加 _2 / _3 ……"""
    seen: dict[str, int] = {}
    out: list[str] = []
    for name in names:
        if name not in seen:
            seen[name] = 1
            out.append(name)
        else:
            seen[name] += 1
            out.append(f"{name}_{seen[name]}")
    return out


def _normalise_name(name: str) -> str:
    return name.strip().replace("T(K)", "T").replace("(K)", "")


def read_profile(path, coord=None):
    """读取单个剖面条目，返回 (columns, rows)。

    coord: 若给出，则把第一列强制重命名（如中心线文件传 "x/d"）。
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    header_idx = None
    for i, line in enumerate(lines):
        if _is_numeric_row(line.split()):
            header_idx = i - 1
            break
    if header_idx is None or header_idx < 0:
        raise ValueError(f"{path.name}: 未找到数值数据行")

    columns = [_normalise_name(c) for c in lines[header_idx].split()]
    if coord:
        columns[0] = coord
    columns = _dedup(columns)

    rows = []
    for line in lines[header_idx + 1:]:
        tokens = line.split()
        if not _is_numeric_row(tokens):
            continue
        rows.append([_to_float(t) for t in tokens])

    width = min(len(columns), min((len(r) for r in rows), default=0))
    return columns[:width], [r[:width] for r in rows]


def parse_station(name):
    """从文件名解析 (火焰, x/d)。D15 -> ('D', 15.0)；D075 -> ('D', 7.5)；DCL -> ('D', None)。"""
    stem = Path(name).name.split(".")[0]
    flame = stem[0].upper()
    rest = stem[1:]
    if rest.upper() == "CL":
        return flame, None
    digits = "".join(ch for ch in rest if ch.isdigit())
    if not digits:
        return flame, None
    value = float(digits)
    # 文件名省略了小数点：D075 -> 7.5（前导 0 表示有小数位），D75 -> 75
    if len(digits) >= 3 and digits.startswith("0"):
        value = value / 10.0
    return flame, value


def write_csv(columns, rows, out_path, meta=None):
    """把剖面条目写成 CSV，首部用 # 注释记录来源。"""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        if meta:
            for key, value in meta.items():
                fh.write(f"# {key}: {value}\n")
        writer = csv.writer(fh)
        writer.writerow(columns)
        writer.writerows(rows)
    return out_path


def read_profile_df(path, coord=None):
    """读取为 pandas.DataFrame（需要安装 pandas）。"""
    import pandas as pd

    columns, rows = read_profile(path, coord=coord)
    return pd.DataFrame(rows, columns=columns)
