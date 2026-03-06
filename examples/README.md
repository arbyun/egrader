# Windows Compatibility 'Patch'

This README documents every change I made to be able to run `egrader` on Windows without WSL/Linux and gives exact step-by-step instructions to run tests and generate reports.

## 1) What was changed for Windows compatibility

### 1.1 Replaced `sh` with `subprocess` for Git commands

File changed: `src/egrader/git.py`

- Removed Linux/macOS-only `sh` dependency and imports.
- Implemented Git calls using Python standard library `subprocess.run(...)`.
- Kept the same public helpers:
  - `git(*args)`
  - `git_at(repo_path, *args)`
- Preserved explicit error wrapping with `GitError` so CLI error messages stay consistent.

Why: package `sh` fails on Windows (`ImportError: sh ... only supported on Linux and macOS`).

### 1.2 Updated CLI exception handling

File changed: `src/egrader/cli_bin.py`

- Replaced `from sh import ErrorReturnCode` with `from .git import GitError`.
- Updated the main exception handling tuple to catch `GitError`.

Why: after moving Git execution away from `sh`, CLI should catch project-level Git errors, not `sh` internals.

### 1.3 Removed `sh` from dependencies

File changed: `pyproject.toml`

- Removed runtime dependency: `"sh >= 2.0.0"`.
- Removed `"sh"` from `tool.mypy.overrides` because it is no longer imported.
- Verified TOML parses correctly.

Why: avoid pulling a non-Windows-compatible dependency.

### 1.4 Accepted native Windows local paths in `students.tsv`

File changed: `src/egrader/types.py`

- In `StudentGit.__init__`, added direct local path detection before URL parsing:
  - `Path(url).exists() and Path(url).is_dir()` => treat as valid local file base path.
- Existing URL behavior (`file://`, `http(s)://`) remains intact.

Why: strings like `C:\\some\\path` were interpreted by `urlparse` as scheme `c`, causing valid local paths to be rejected.

## 2) Validation performed on Windows

### 2.1 Targeted repository plugin tests

Command used:

```powershell
$env:PYTHONPATH='src'
python -m pytest -q -c .pytest_local.ini tests\plugins\test_repo.py
```

Result: `24 passed`.

### 2.2 End-to-end local run (`fetch -> assess -> report`)

Added helper script: `examples/windows_demo_run.py`.

What it does is:
- Creates local sample student Git repos.
- Creates `students.tsv` and `rules.yml`.
- Runs:
  - `egrader fetch ...`
  - `egrader assess ...`
  - `egrader report ... basic`
  - `egrader report ... tsv`
  - `egrader report ... markdown -f`

Generated artifacts should be under `examples/windows_demo/`.

## 3) Exact step-by-step from a new Windows environment

### Step 1: Open terminal in repository root



### Step 2: Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### Step 3: Install project + dev dependencies

```powershell
python -m pip install -e .[dev]
```

### Step 4: Run the targeted tests 

```powershell
$env:PYTHONPATH='src'
python -m pytest -q -c .pytest_local.ini tests\plugins\test_repo.py
```

Expected: all tests pass.

### Step 5: Smoke-test plugin discovery (Optional)

```powershell
$env:PYTHONPATH='src'
python -c "import sys; from egrader.cli_bin import main; sys.argv=['egrader','plugins']; raise SystemExit(main())"
```

Expected: list of repository/inter-repo/report plugins.

### Step 6: Run full local demo and generate reports (Optional)

```powershell
$env:PYTHONPATH='src'
python examples\windows_demo_run.py
```


## 4) Notes

- In `students.tsv`, local paths can be either:
  - relative paths
  - absolute Windows paths (e.g., `C:\\class\\student01`)
- `git` must be installed and available in `PATH`.

## Disclaimer

I'm not entirely sure what removing `sh` does. From my tests, it didn't seem to change anything, but I'm running everything from a Windows environment. Removal is untested in Linux and/or MacOS.