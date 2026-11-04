# dupescan

<!-- ORDER-CTA -->
> **需要定制或代做？** 我承接 Excel 代做（¥50 起）/ 零依赖 Python 脚本定制（¥200 起）/ 影刀·UiBot 机器人（¥500 起）。
> **先报价后付款、无预付款**，微信 / 支付宝结算，询价发 **2383844705@qq.com**（标题写「接单 + 需求类型」）。
> 更多工具与报价见作品集：https://zhiyilang.github.io/


> Find duplicate files on your disk — **fast, zero-dependency, cross-platform.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](dupescan.py)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](dupescan.py)

`dupescan` scans your folders, groups files by **content hash (SHA-256)**, and tells you
exactly how much disk space you can reclaim by deleting redundant copies. It is a single
Python file using **only the standard library** — no `pip install`, no compilation, works
everywhere Python runs.

> 纯标准库、零第三方依赖的单文件重复文件查找工具，跨 Windows / macOS / Linux，
> 按内容 SHA-256 哈希比对，告诉你哪些文件是重复的、能省出多少空间。

---

## Why dupescan?

- 🪶 **One file, no dependencies.** Drop `dupescan.py` anywhere and run it.
- ⚡ **Fast.** Pre-groups by file size, then hashes only same-size candidates; 1 MiB chunked IO.
- 🧠 **Accurate.** Content hash, not filename — finds renamed / moved duplicates.
- 🌐 **Cross-platform.** Same command on Windows, macOS, Linux.
- 📋 **Multiple outputs.** Human text, JSON (for scripts), or Markdown (for reports).
- 🔒 **Safe by default.** Reports only; add `--delete` to actually remove (with confirmation).

## Install / 安装

No install needed. Just download `dupescan.py`:

```bash
# run directly
python dupescan.py /path/to/scan

# or make it a command
cp dupescan.py /usr/local/bin/dupescan   # macOS / Linux
dupescan C:\Users\You\Pictures
```

无需安装，下载 `dupescan.py` 即可：

```bash
python dupescan.py D:\照片备份
```

## Usage / 用法

```bash
python dupescan.py PATH [PATH ...] [options]
```

### Common examples / 常用示例

```bash
# 1. Scan one folder (default text report)
python dupescan.py ~/Photos

# 2. Scan several folders at once
python dupescan.py D:\备份 C:\Users\You\Downloads

# 3. Only images, ignore tiny files
python dupescan.py ~/Pictures --pattern "*.jpg" --min-size 1024

# 4. Skip a cache directory
python dupescan.py . --exclude ./node_modules --exclude ./venv

# 5. Machine-readable output (JSON / Markdown)
python dupescan.py ~/Docs --json
python dupescan.py ~/Docs --md > report.md

# 6. Only the 10 largest duplicate groups
python dupescan.py ~/Videos --top 10

# 7. Actually delete redundant copies (keeps the first of each group)
python dupescan.py ~/Downloads --delete
python dupescan.py ~/Downloads --delete --yes   # no prompt (CI / automation)
```

### Options / 参数

| Option | Description |
|--------|-------------|
| `PATH ...` | One or more directories/files to scan |
| `--min-size N` | Ignore files smaller than N bytes (default 1) |
| `--pattern PAT` | Only scan files matching glob, e.g. `"*.jpg"` |
| `--exclude DIR` | Skip a directory (repeatable) |
| `--no-empty` | Ignore zero-byte files |
| `--top N` | Show only the N largest duplicate groups |
| `--json` | Output JSON |
| `--md` | Output Markdown |
| `--delete` | Delete all but the first file in each duplicate group |
| `--yes` | Assume "yes" for `--delete` (non-interactive) |
| `-q, --quiet` | Suppress progress output |

## Example output / 输出示例

```
======================================================================
DUPLICATE FILES REPORT
======================================================================

[1] 3 copies  |  2.34 MB each  |  reclaim 4.68 MB
    - /Users/you/Pictures/IMG_001.jpg
    - /Users/you/Downloads/IMG_001 (1).jpg
    - /Users/you/Backup/photos/IMG_001.jpg

======================================================================
SUMMARY: 3 duplicate files across 1 groups, reclaim 4.68 MB
======================================================================
```

## How it works / 原理

1. Walk every path, collect candidate files (apply `--pattern` / `--exclude` / `--min-size`).
2. **Pre-group by file size** — different sizes can never be duplicates, so this is a cheap filter.
3. For each size group with ≥2 files, compute **SHA-256** content hashes (1 MiB chunks).
4. Files sharing the same hash are duplicates; the first is kept, the rest are reclaimable.
5. Report total reclaimable space per group and overall.

> 先按文件大小分组（大小不同必非重复），再对同一大小的候选做 SHA-256 内容哈希，
> 同哈希即重复。默认只报告、不删除；加 `--delete` 才真正清理（带确认）。

## Use cases / 适用场景

- 🧹 Reclaim disk space from photo / backup / download clutter.
- 🔄 Find duplicates after merging folders or syncing devices.
- 📦 CI cleanup checks, or feeding JSON output into other tooling.
- 🔍 Audit storage before archiving.

## License

[MIT](LICENSE) — free for personal and commercial use.

---

💝 If dupescan saved you some disk (or time), consider supporting its development:
**爱发电 / Afdian → https://afdian.com/a/Zhiyilang** · ⭐ Star the repo!

<!-- cross-links -->

## 🔗 More zero-dependency tools

All of these are single-file, pure Python-stdlib CLIs — offline, no `pip install`, cross-platform:

- **billfusion** — Bill / CSV merging · <https://github.com/Zhiyilang/billfusion>
- **lanshare** — LAN file transfer · <https://github.com/Zhiyilang/lanshare>
- **csvdiff** — CSV / JSON diff · <https://github.com/Zhiyilang/csvdiff>
- **md2html** — Markdown to HTML · <https://github.com/Zhiyilang/md2html>
- **dirsize** — Directory size analyzer · <https://github.com/Zhiyilang/dirsize>

Full portfolio & docs: <https://zhiyilang.github.io/>
