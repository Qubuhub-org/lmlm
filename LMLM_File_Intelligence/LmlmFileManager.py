#!/usr/bin/env python3
"""
LMLM File Intelligence
Local-first file study, safe organization, and document merging.

Repository safety:
- Never edits, moves, or deletes tracked repository files.
- Repository organization is a proposed plan/report only.
- Merge outputs are written outside the selected source tree.
- Never commits, pushes, resets, or changes Git history.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

APP_NAME = "LMLM File Intelligence"
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules",
    "target", "dist", "build", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".next", ".idea", ".vscode",
}
CATEGORIES = {
    "PDFs": {".pdf"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".tif", ".tiff", ".svg"},
    "Documents": {".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".rst", ".pages"},
    "Spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
    "Audio": {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"},
    "Video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"},
    "Code": {".py", ".rs", ".go", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".swift",
             ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".rb", ".sh", ".ps1", ".applescript",
             ".sql", ".toml", ".yaml", ".yml", ".json", ".xml", ".html", ".css"},
}
TEXT_MERGE_EXTS = {".txt", ".md", ".rst", ".csv", ".log"}
MAX_TEXT_FILE_BYTES = 20 * 1024 * 1024


def stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def category_for(path: Path) -> str:
    suffix = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "Other"


def git_root(path: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True, timeout=10,
        )
        return Path(result.stdout.strip()).resolve()
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def git_snapshot(root: Path) -> dict:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short", "--branch", "--untracked-files=all"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode:
        return {"available": False, "error": result.stderr.strip()}
    lines = result.stdout.splitlines()
    return {
        "available": True,
        "branch_and_status": lines[0] if lines else "",
        "entries": lines[1:],
        "tracked_changes": sum(1 for line in lines[1:] if not line.startswith("??")),
        "untracked": sum(1 for line in lines[1:] if line.startswith("??")),
    }


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(
            d for d in dirs
            if d not in SKIP_DIRS and not d.startswith(".LMLM-")
        )
        current_path = Path(current)
        for name in sorted(files):
            candidate = current_path / name
            if candidate.is_symlink():
                continue
            yield candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_inventory(root: Path) -> dict:
    files = []
    counts = Counter()
    total_bytes = 0
    duplicates = defaultdict(list)
    errors = []

    for path in iter_files(root):
        try:
            stat = path.stat()
            category = category_for(path)
            digest = sha256(path) if stat.st_size <= 512 * 1024 * 1024 else None
            rel = str(path.relative_to(root))
            item = {
                "path": rel,
                "name": path.name,
                "extension": path.suffix.lower(),
                "category": category,
                "size_bytes": stat.st_size,
                "modified": dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "sha256": digest,
            }
            files.append(item)
            counts[category] += 1
            total_bytes += stat.st_size
            if digest:
                duplicates[digest].append(rel)
        except (OSError, PermissionError) as exc:
            errors.append(f"{path}: {exc}")

    duplicate_groups = [paths for paths in duplicates.values() if len(paths) > 1]
    return {
        "root": str(root),
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "category_counts": dict(sorted(counts.items())),
        "files": files,
        "duplicate_groups": duplicate_groups,
        "errors": errors,
    }


def report_directory(root: Path, is_repo: bool) -> Path:
    # Keep reports and merge outputs outside the source tree.
    parent = Path.home() / "Documents" / "LMLM-FileIntelligence"
    parent.mkdir(parents=True, exist_ok=True)
    label = root.name or "selected-folder"
    if is_repo:
        label += "-repo"
    destination = parent / f"{label}-{stamp()}"
    destination.mkdir(parents=True, exist_ok=False)
    return destination


def write_study_report(inventory: dict, destination: Path, repo_data: dict | None) -> tuple[Path, Path]:
    json_path = destination / "inventory.json"
    md_path = destination / "STUDY_REPORT.md"
    json_path.write_text(json.dumps({"inventory": inventory, "git": repo_data}, indent=2), encoding="utf-8")

    lines = [
        f"# {APP_NAME} — Study report",
        "",
        f"- Root: `{inventory['root']}`",
        f"- Generated: {inventory['generated_at']}",
        f"- Files studied: **{inventory['file_count']}**",
        f"- Total size: **{inventory['total_bytes']:,} bytes**",
        "",
        "## File categories",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in inventory["category_counts"].items():
        lines.append(f"| {category} | {count} |")
    lines += ["", "## Duplicate candidates", ""]
    if inventory["duplicate_groups"]:
        for group in inventory["duplicate_groups"]:
            lines.append("- " + ", ".join(f"`{p}`" for p in group))
    else:
        lines.append("No duplicate files detected among files hashed (files up to 512 MiB).")
    if repo_data is not None:
        lines += ["", "## Git repository status", ""]
        if repo_data.get("available"):
            lines += [
                f"- Branch/status: `{repo_data.get('branch_and_status', '')}`",
                f"- Modified/deleted tracked entries: {repo_data.get('tracked_changes', 0)}",
                f"- Untracked entries: {repo_data.get('untracked', 0)}",
                "",
            ]
            lines.extend(f"- `{entry}`" for entry in repo_data.get("entries", []))
            if not repo_data.get("entries"):
                lines.append("Working tree clean.")
        else:
            lines.append(f"Git status unavailable: {repo_data.get('error', 'unknown error')}")
    if inventory["errors"]:
        lines += ["", "## Read errors", ""]
        lines.extend(f"- {error}" for error in inventory["errors"])
    lines += [
        "",
        "## Safety notes",
        "",
        "- This report is an inventory, not a code-quality or security certification.",
        "- Hidden/system/build directories listed in the tool configuration are excluded.",
        "- Repository source files were not moved or modified.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(2, 10000):
        candidate = path.with_name(f"{path.stem} ({index}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Unable to find a free destination for {path.name}")


def organize_local_root_files(root: Path) -> list[str]:
    """Move only direct child files in a normal local folder; never recurse."""
    moved = []
    for source in sorted(root.iterdir()):
        if not source.is_file() or source.is_symlink() or source.name.startswith("."):
            continue
        category = category_for(source)
        destination_dir = root / category
        destination_dir.mkdir(exist_ok=True)
        destination = unique_path(destination_dir / source.name)
        shutil.move(str(source), str(destination))
        moved.append(f"{source.name} -> {category}/{destination.name}")
    return moved


def proposed_repo_arrangement(inventory: dict) -> dict:
    """Plan only. Never move repository files because paths may be build/import contracts."""
    plan = defaultdict(list)
    for item in inventory["files"]:
        plan[item["category"]].append(item["path"])
    return dict(sorted(plan.items()))


def merge_selected_files(root: Path, output_dir: Path) -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except Exception as exc:
        raise RuntimeError(f"File picker unavailable: {exc}") from exc

    window = tk.Tk()
    window.withdraw()
    selected = filedialog.askopenfilenames(
        title="Select files to merge (choose one file type per merge)",
        initialdir=str(root),
        filetypes=[
            ("PDF documents", "*.pdf"),
            ("Text / Markdown / CSV / logs", "*.txt *.md *.rst *.csv *.log"),
            ("All files", "*"),
        ],
    )
    window.destroy()
    paths = [Path(p) for p in selected]
    if not paths:
        return None

    extensions = {p.suffix.lower() for p in paths}
    if len(extensions) != 1:
        raise ValueError("Select files with the same extension in one merge operation.")
    extension = next(iter(extensions))
    out = output_dir / f"merged-{stamp()}{extension}"

    if extension == ".pdf":
        try:
            from pypdf import PdfReader, PdfWriter
            writer = PdfWriter()
            for path in paths:
                reader = PdfReader(str(path), strict=False)
                for page in reader.pages:
                    writer.add_page(page)
            with out.open("wb") as stream:
                writer.write(stream)
        except ImportError:
            pdfunite = shutil.which("pdfunite")
            if not pdfunite:
                raise RuntimeError("PDF merge needs `pypdf` (pip install pypdf) or Poppler `pdfunite`.")
            subprocess.run([pdfunite, *map(str, paths), str(out)], check=True)
    elif extension in TEXT_MERGE_EXTS:
        with out.open("w", encoding="utf-8", newline="") as target:
            for index, path in enumerate(paths, start=1):
                if path.stat().st_size > MAX_TEXT_FILE_BYTES:
                    raise ValueError(f"Refusing to merge text file over 20 MiB: {path.name}")
                target.write(f"\n\n{'=' * 72}\nFILE {index}: {path.name}\n{'=' * 72}\n\n")
                target.write(path.read_text(encoding="utf-8-sig", errors="replace"))
                target.write("\n")
    else:
        raise ValueError(f"Unsupported merge type: {extension or '(no extension)'}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--root", required=True, help="Folder to study or manage")
    parser.add_argument("--mode", choices=("study", "organize", "merge", "full"), default="study")
    parser.add_argument("--confirm-local-moves", action="store_true",
                        help="Required to physically organize a non-repository folder")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: Not a folder: {root}", file=sys.stderr)
        return 2

    repo = git_root(root)
    is_repo = repo is not None
    # If a subfolder was selected, operate on the actual repository root in repo mode.
    if is_repo:
        root = repo

    output_dir = report_directory(root, is_repo)
    inventory = build_inventory(root)
    git_data = git_snapshot(root) if is_repo else None
    md_report, json_report = write_study_report(inventory, output_dir, git_data)

    actions = []
    actions.append(f"Studied {inventory['file_count']} files ({inventory['total_bytes']:,} bytes).")
    actions.append(f"Report: {md_report}")
    actions.append(f"Inventory JSON: {json_report}")

    if args.mode in ("organize", "full"):
        if is_repo:
            plan = proposed_repo_arrangement(inventory)
            plan_path = output_dir / "REPOSITORY_ARRANGEMENT_PLAN.md"
            plan_lines = ["# Repository arrangement plan", "",
                          "This is a classification plan only. No repository files were moved.", ""]
            for category, paths in plan.items():
                plan_lines += [f"## {category}", ""]
                plan_lines.extend(f"- `{path}`" for path in paths)
                plan_lines.append("")
            plan_path.write_text("\n".join(plan_lines), encoding="utf-8")
            actions.append(f"Repository arrangement plan (read-only): {plan_path}")
        elif args.confirm_local_moves:
            moved = organize_local_root_files(root)
            actions.append(f"Moved {len(moved)} top-level local files into category folders.")
            actions.extend(moved)
        else:
            actions.append("Local moves skipped: rerun with --confirm-local-moves to enable physical organization.")

    if args.mode in ("merge", "full"):
        merged = merge_selected_files(root, output_dir)
        actions.append(f"Merged output: {merged}" if merged else "Merge cancelled; no source files changed.")

    print(APP_NAME)
    print(f"Scope: {'Git repository (read-only organization)' if is_repo else 'Local folder'}")
    print("\n".join(f"- {item}" for item in actions))
    print(f"\nOutputs saved outside the source folder: {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
