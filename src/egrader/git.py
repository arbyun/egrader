"""Functions for handling Git functionality."""

from pathlib import Path
from subprocess import CalledProcessError, run


class GitError(Exception):
    """Error raised when a Git command fails."""


def git(*args):
    """Run git with the specified arguments."""
    try:
        completed = run(
            ["git", "--no-pager", *[str(arg) for arg in args]],
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()
    except CalledProcessError as erc:
        cmd = " ".join([str(part) for part in erc.cmd])
        stderr = (erc.stderr or "").strip()
        raise GitError(
            f"The following error occurred when executing the {cmd!r} command:"
            f"\n\n{stderr}"
        ) from erc


def git_at(repo_path, *args):
    """Run git at location given by repo_path with the specified arguments."""
    return git("-C", Path(repo_path), *args)
