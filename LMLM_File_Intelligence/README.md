# LMLM File Intelligence

A local-first file study, organization, and document-merging utility for macOS.

## Files

- `LmlmFileManager.py` — Python engine; works with local folders and Git repositories.
- `LmlmFileManager.applescript` — macOS launcher with folder and operation selection.

## Requirements

- macOS with Python 3.
- Git is optional; it is detected automatically for repository mode.
- PDF merging: install `pypdf` (`python3 -m pip install pypdf`) or Poppler (`pdfunite`).
- Text merge supports `.txt`, `.md`, `.rst`, `.csv`, and `.log`.

## Run from Terminal

```bash
python3 LmlmFileManager.py --root "$HOME/Downloads" --mode study
python3 LmlmFileManager.py --root "$HOME/Downloads" --mode organize --confirm-local-moves
python3 LmlmFileManager.py --root "/path/to/repository" --mode study
python3 LmlmFileManager.py --root "/path/to/repository" --mode organize
python3 LmlmFileManager.py --root "/path/to/folder" --mode merge
```

`merge` opens a multi-select file picker. Select files of one type at a time.

## Modes

- **study** — recursively inventories files, classifies extensions, records sizes and modification times, hashes files up to 512 MiB to identify duplicate candidates, and captures Git status when applicable.
- **organize** — for a normal local folder, moves only direct child files into category folders. Requires `--confirm-local-moves`. For a Git repository, creates a proposed category plan and does not move repository files.
- **merge** — merges selected PDFs or selected text/Markdown/CSV/log files. Source files are never modified.
- **full** — study + safe organization behavior + selected-file merge.

## Safety model

- Never deletes files.
- Never overwrites a destination; it adds a numbered suffix.
- Does not follow symlinks.
- Excludes `.git`, common build/cache folders, virtual environments, and dependency directories from recursive study.
- Never moves tracked or untracked files in a Git repository.
- Never commits, pushes, resets, stages, or rewrites Git history.
- Reports and merged outputs are written to `~/Documents/LMLM-FileIntelligence/`, outside the selected source tree.
- Local organization is non-recursive and requires explicit confirmation.

## Limitations

- “Study” is a structural inventory, not semantic understanding or malware/security scanning.
- Repository arrangement is a suggested classification plan, not an automatic source-code refactor.
- PDF merge requires `pypdf` or `pdfunite`.
- Large files above 512 MiB are inventoried but not hashed.
