"""从 TNF Workshop 下载 Sandia/TUD piloted CH4-air（Flame D）数据存档。

TNF 网站无需注册 / 无需登录，数据是公开直链。本脚本只用标准库 urllib，
新机器上一条命令即可完整复现数据环境。

用法
----
    python scripts/fetch_flameD.py                  # 下载到 data/raw/
    python scripts/fetch_flameD.py --extract        # 下载并解压
    python scripts/fetch_flameD.py --force          # 强制重下
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://tnfworkshop.org/wp-content/uploads/2019/02/"

FILES = {
    "SandiaPilotDoc21.pdf": "实验文档（构型、边界条件、不确定度、测量标定说明）",
    "pmCDEF.zip": "火焰 C/D/E/F 标量数据（Raman/Rayleigh/LIF，单发 + 系综平均）",
    "LongRecordsFlameD.zip": "Flame D 长序列单点数据（统计量与 PDF 用）",
    "TUD_LDV_DEF.zip": "TUD LDV 速度数据（Flame D/E/F 轴向与径向剖面）",
}

# 粗略的完整性下限（字节），防止把错误页当成数据存下来
MIN_BYTES = {
    "SandiaPilotDoc21.pdf": 150_000,
    "pmCDEF.zip": 6_000_000,
    "LongRecordsFlameD.zip": 2_500_000,
    "TUD_LDV_DEF.zip": 20_000,
}


def download(name: str, dest: Path, force: bool = False) -> Path:
    target = dest / name
    if target.exists() and not force:
        print(f"  [skip ] {name} 已存在 ({target.stat().st_size:,} B)")
        return target

    url = BASE + name
    print(f"  [get  ] {name}")
    request = urllib.request.Request(url, headers={"User-Agent": "cfd-portfolio/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as fh:
        while True:
            chunk = response.read(1 << 16)
            if not chunk:
                break
            fh.write(chunk)

    size = target.stat().st_size
    if size < MIN_BYTES.get(name, 0):
        target.unlink(missing_ok=True)
        raise RuntimeError(f"{name} 只有 {size:,} B，疑似下载不完整，已删除")
    print(f"         -> {size:,} B")
    return target


def extract(zip_path: Path) -> None:
    out = zip_path.with_suffix("")
    print(f"  [unzip] {zip_path.name} -> {out.name}/")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="下载 TNF Flame D 数据存档")
    parser.add_argument("--dest", default="data/raw", help="下载目录，默认 data/raw")
    parser.add_argument("--extract", action="store_true", help="下载后解压 zip")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件")
    args = parser.parse_args(argv)

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    print("TNF Workshop · Sandia/TUD piloted CH4/air flames (Release 2.0, 2003-01)")
    print(f"目标目录: {dest.resolve()}")
    failures = []
    for name in FILES:
        try:
            path = download(name, dest, force=args.force)
            if args.extract and name.endswith(".zip"):
                extract(path)
        except Exception as exc:  # noqa: BLE001
            failures.append((name, str(exc)))
            print(f"  [FAIL ] {name}: {exc}", file=sys.stderr)

    print()
    if failures:
        print(f"完成，但有 {len(failures)} 个文件失败：")
        for name, err in failures:
            print(f"  - {name}: {err}")
        return 1

    print("下载完成。下一步： python scripts/probe_flamed.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
