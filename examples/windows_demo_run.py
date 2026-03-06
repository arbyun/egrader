from __future__ import annotations

from datetime import datetime
from pathlib import Path
from subprocess import run
import os
import shutil
import stat
import sys

from egrader.cli_bin import main


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def on_rm_error(func, path, exc_info) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_tree(path: Path) -> None:
    shutil.rmtree(path, onexc=on_rm_error)


def run_cmd(args: list[str], *, capture: bool = False) -> None:
    log(f"[CMD] {' '.join(args)}")
    result = run(args, check=True, capture_output=capture, text=True)
    if capture and result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            log(f"[OUT] {line}")


def run_egrader(argv: list[str]) -> None:
    log(f"[STEP] Running egrader command: {' '.join(argv[1:])}")
    sys.argv = argv
    rc = main()
    if rc != 0:
        raise SystemExit(rc)
    log("[OK] Command finished successfully")


def main_demo() -> None:
    log("[STEP] Preparing paths")
    root = Path("examples/windows_demo").resolve()
    base = root / "student_bases"
    out = root / "out_windows_demo"
    rules = root / "rules.yml"
    urls = root / "students.tsv"

    log(f"[INFO] Demo root: {root}")

    if root.exists():
        log("[STEP] Removing previous demo folder")
        remove_tree(root)
    base.mkdir(parents=True)
    log("[OK] Created fresh demo folder structure")

    students = [
        ("s1001", "s1001@example.org"),
        ("s1002", "s1002@example.org"),
    ]
    repo_name = "LP1Aula01"

    log("[STEP] Creating local student repositories")
    for sid, email in students:
        student_base = base / sid
        student_base.mkdir(parents=True)
        repo = student_base / repo_name
        log(f"[INFO] Initializing repository for {sid}: {repo}")

        run_cmd(["git", "init", str(repo)], capture=True)
        run_cmd(["git", "-C", str(repo), "config", "user.name", sid])
        run_cmd(["git", "-C", str(repo), "config", "user.email", email])

        (repo / "README.md").write_text(f"# Repo for {sid}\n", encoding="utf-8")
        (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        log(f"[INFO] Wrote README.md and .gitignore for {sid}")

        run_cmd(["git", "-C", str(repo), "add", "."])
        run_cmd(["git", "-C", str(repo), "commit", "-m", "initial commit"])

    log("[STEP] Adding second commit to student s1002 for grading variance")
    repo2 = base / "s1002" / repo_name
    (repo2 / "extra.txt").write_text("extra\n", encoding="utf-8")
    run_cmd(["git", "-C", str(repo2), "add", "."])
    run_cmd(["git", "-C", str(repo2), "commit", "-m", "second commit"])

    log("[STEP] Writing demo rules.yml")
    rules.write_text(
        """- repo: LP1Aula01
  weight: 10
  assessments:
  - name: repo_exists
    weight: 0.1
  - name: min_commits
    weight: 0.9
    params:
      minimum: 2
  - name: files_exist
    weight: 0.2
    params:
      filenames:
      - README.md
      - .gitignore
""",
        encoding="utf-8",
    )

    log("[STEP] Writing demo students.tsv")
    with urls.open("w", encoding="utf-8") as f:
        for sid, email in students:
            f.write(f"{sid}\t{email}\t{(base / sid).as_posix()}\n")
    log(f"[OK] Wrote: {urls}")

    commands = [
        ["egrader", "fetch", str(urls), str(rules), str(out)],
        ["egrader", "assess", str(rules), str(out)],
        ["egrader", "report", str(out), "basic"],
        ["egrader", "report", str(out), "tsv"],
        ["egrader", "report", str(out), "markdown", "-f"],
    ]

    log("[STEP] Running egrader workflow")
    for argv in commands:
        run_egrader(argv)

    log("[DONE] Windows demo run completed")
    log(f"[DONE] Output root: {root}")


if __name__ == "__main__":
    main_demo()
