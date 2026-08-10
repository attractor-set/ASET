#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def fail(message: str) -> int:
    print(f"REPOSITORY_SOURCE_IDENTITY_ERROR={message}")
    print("REPOSITORY_SOURCE_IDENTITY=FAIL")
    return 1


def main() -> int:
    inside = git("rev-parse", "--is-inside-work-tree")
    if inside.returncode or inside.stdout.strip() != "true":
        return fail("not a Git worktree")

    head = git("rev-parse", "HEAD")
    if head.returncode:
        return fail("cannot resolve HEAD")
    commit = head.stdout.strip()

    tree = git("rev-parse", "HEAD^{tree}")
    if tree.returncode:
        return fail("cannot resolve HEAD tree")
    tree_sha = tree.stdout.strip()

    whitespace = git("diff", "--check")
    if whitespace.returncode:
        detail = (whitespace.stdout + whitespace.stderr).strip()
        return fail("git diff --check failed" + (f": {detail}" if detail else ""))

    worktree = git("diff", "--quiet", "HEAD", "--")
    if worktree.returncode:
        return fail("tracked worktree differs from HEAD")

    index = git("diff", "--cached", "--quiet", "HEAD", "--")
    if index.returncode:
        return fail("index differs from HEAD")

    print(f"REPOSITORY_SOURCE_COMMIT={commit}")
    print(f"REPOSITORY_SOURCE_TREE={tree_sha}")
    print("TRACKED_WORKTREE_CLEAN=PASS")
    print("TRACKED_INDEX_CLEAN=PASS")
    print("REPOSITORY_SOURCE_IDENTITY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
