#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dupescan - Find duplicate files on your disk. Fast, zero-dependency.

Pure Python standard library. No pip install required.
Works on Windows / macOS / Linux.

Scans one or more paths, groups files by content hash (SHA-256), and reports
how much disk space you can reclaim by removing redundant copies.

Author: Zhiyilang
License: MIT
"""

import argparse
import fnmatch
import hashlib
import json
import os
import sys

CHUNK = 1 << 20  # 1 MiB read buffer


def human(n):
    """Format a byte count into a human readable string."""
    if n < 1024:
        return "%d B" % n
    units = ["KB", "MB", "GB", "TB", "PB"]
    f = float(n)
    for u in units:
        f /= 1024.0
        if f < 1024.0 or u == units[-1]:
            return "%.2f %s" % (f, u)
    return "%d B" % n


def sha256_of(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(CHUNK), b""):
                h.update(block)
    except (OSError, IOError):
        return None
    return h.digest()


def collect(paths, min_size, pattern, excludes, no_empty, quiet):
    """Walk all paths and return a list of (abspath, size) for candidate files."""
    files = []
    seen_dirs = set()
    total = 0
    for root in paths:
        root = os.path.abspath(root)
        for dirpath, dirnames, filenames in os.walk(root):
            # prune excluded directories in place
            kept = []
            for d in dirnames:
                full = os.path.join(dirpath, d)
                if any(full == ex or full.startswith(ex + os.sep) for ex in excludes):
                    continue
                kept.append(d)
            dirnames[:] = kept
            for name in filenames:
                full = os.path.join(dirpath, name)
                if pattern and not fnmatch.fnmatch(name, pattern):
                    continue
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                if st.st_size < min_size:
                    continue
                if no_empty and st.st_size == 0:
                    continue
                files.append((full, st.st_size))
                total += 1
                if not quiet and total % 2000 == 0:
                    sys.stderr.write("\r scanned %d files ..." % total)
                    sys.stderr.flush()
    if not quiet:
        sys.stderr.write("\r scanned %d files.\n" % total)
    return files


def find_duplicates(files, quiet):
    """Group files by size then by hash; return (dup_groups, errors)."""
    by_size = {}
    for path, size in files:
        by_size.setdefault(size, []).append(path)

    dup_groups = []
    hashed = 0
    for size, group in by_size.items():
        if len(group) < 2:
            continue
        by_hash = {}
        for path in group:
            digest = sha256_of(path)
            if digest is None:
                continue
            by_hash.setdefault(digest, []).append(path)
            hashed += 1
            if not quiet and hashed % 500 == 0:
                sys.stderr.write("\r hashed %d files ..." % hashed)
                sys.stderr.flush()
        for digest, members in by_hash.items():
            if len(members) > 1:
                dup_groups.append((size, members))
    if not quiet:
        sys.stderr.write("\r hashed %d files.\n" % hashed)
    return dup_groups


def build_report(dup_groups, top):
    dup_groups.sort(key=lambda g: g[0] * (len(g[1]) - 1), reverse=True)
    if top:
        dup_groups = dup_groups[:top]
    total_files = 0
    total_wasted = 0
    for size, members in dup_groups:
        total_files += len(members)
        total_wasted += size * (len(members) - 1)
    return dup_groups, total_files, total_wasted


def print_text(dup_groups, total_files, total_wasted):
    if not dup_groups:
        print("No duplicate files found.")
        return
    print("=" * 70)
    print("DUPLICATE FILES REPORT")
    print("=" * 70)
    for i, (size, members) in enumerate(dup_groups, 1):
        wasted = size * (len(members) - 1)
        print("\n[%d] %d copies  |  %s each  |  reclaim %s"
              % (i, len(members), human(size), human(wasted)))
        for m in members:
            print("    - %s" % m)
    print("\n" + "=" * 70)
    print("SUMMARY: %d duplicate files across %d groups, reclaim %s"
          % (total_files, len(dup_groups), human(total_wasted)))
    print("=" * 70)


def print_json(dup_groups, total_files, total_wasted):
    out = {
        "summary": {
            "duplicate_files": total_files,
            "groups": len(dup_groups),
            "reclaimable_bytes": total_wasted,
            "reclaimable_human": human(total_wasted),
        },
        "groups": [
            {"size_bytes": size, "copies": len(members), "files": members}
            for size, members in dup_groups
        ],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def print_md(dup_groups, total_files, total_wasted):
    if not dup_groups:
        print("No duplicate files found.")
        return
    print("# Duplicate Files Report\n")
    print("- **Duplicate files:** %d" % total_files)
    print("- **Groups:** %d" % len(dup_groups))
    print("- **Reclaimable:** %s\n" % human(total_wasted))
    for i, (size, members) in enumerate(dup_groups, 1):
        wasted = size * (len(members) - 1)
        print("## Group %d — %d copies, %s each, reclaim %s\n"
              % (i, len(members), human(size), human(wasted)))
        for m in members:
            print("- `%s`" % m)
        print()


def delete_duplicates(dup_groups, assume_yes):
    deleted = 0
    freed = 0
    for size, members in dup_groups:
        keep = members[0]
        for victim in members[1:]:
            if not assume_yes:
                ans = input("Delete %s ? [y/N] " % victim)
                if ans.lower() != "y":
                    continue
            try:
                os.remove(victim)
                deleted += 1
                freed += size
                print("deleted: %s" % victim)
            except OSError as e:
                print("FAILED %s: %s" % (victim, e))
    print("\nDeleted %d files, freed %s." % (deleted, human(freed)))


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="dupescan",
        description="Find duplicate files on your disk (zero-dependency).",
    )
    p.add_argument("paths", nargs="+", help="directories or files to scan")
    p.add_argument("--min-size", type=int, default=1,
                   help="ignore files smaller than N bytes (default 1)")
    p.add_argument("--pattern", default="",
                   help="only scan files matching glob, e.g. '*.jpg'")
    p.add_argument("--exclude", action="append", default=[],
                   help="skip this directory (repeatable)")
    p.add_argument("--no-empty", action="store_true",
                   help="ignore zero-byte files")
    p.add_argument("--top", type=int, default=0,
                   help="only show the N largest duplicate groups")
    p.add_argument("--json", action="store_true", help="output JSON")
    p.add_argument("--md", action="store_true", help="output Markdown")
    p.add_argument("--delete", action="store_true",
                   help="DELETE all but the first file in each group")
    p.add_argument("--yes", action="store_true",
                   help="assume yes for --delete (non-interactive)")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="suppress progress output")
    args = p.parse_args(argv)

    excludes = [os.path.abspath(x) for x in args.exclude]
    files = collect(args.paths, args.min_size, args.pattern,
                    excludes, args.no_empty, args.quiet)
    dup_groups = find_duplicates(files, args.quiet)
    dup_groups, total_files, total_wasted = build_report(dup_groups, args.top)

    if args.delete:
        delete_duplicates(dup_groups, args.yes)
        return 0

    if args.json:
        print_json(dup_groups, total_files, total_wasted)
    elif args.md:
        print_md(dup_groups, total_files, total_wasted)
    else:
        print_text(dup_groups, total_files, total_wasted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
