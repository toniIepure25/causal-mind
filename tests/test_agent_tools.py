from __future__ import annotations

from pathlib import Path

import pytest

from causal_mind.agent.tools import (
    execute_tool,
    run_bash,
    run_edit,
    run_glob,
    run_grep,
    run_read,
    run_write,
)


@pytest.fixture()
def workdir(tmp_path: Path) -> Path:
    (tmp_path / "a.txt").write_text("alpha\nbeta\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("gamma\n", encoding="utf-8")
    return tmp_path


def test_read_write_roundtrip(workdir: Path) -> None:
    result = run_write("new.txt", "content", workdir)
    assert result.ok
    assert run_read("new.txt", workdir).output == "content"


def test_read_outside_workdir_denied(workdir: Path) -> None:
    result = run_read("/etc/hostname", workdir)
    assert not result.ok
    assert "escapes workdir" in result.output


def test_write_outside_workdir_denied(workdir: Path) -> None:
    result = run_write("../escape.txt", "x", workdir)
    assert not result.ok


def test_bash_runs_in_workdir(workdir: Path) -> None:
    result = run_bash("pwd", workdir)
    assert result.ok
    assert workdir.resolve().as_posix() in result.output


def test_bash_denies_git_push(workdir: Path) -> None:
    result = run_bash("git push origin main", workdir)
    assert not result.ok
    assert "denied" in result.output


def test_bash_denies_kubectl(workdir: Path) -> None:
    result = run_bash("kubectl get pods", workdir)
    assert not result.ok


def test_bash_denies_credential_paths(workdir: Path) -> None:
    result = run_bash("cat /home/jovyan/.runai/authentication.json", workdir)
    assert not result.ok
    result = run_bash("ls ~/.ssh", workdir)
    assert not result.ok


def test_bash_denies_outside_rm(workdir: Path) -> None:
    result = run_bash("rm -rf /tmp/some-other-dir", workdir)
    assert not result.ok
    assert "outside workdir" in result.output


def test_bash_allows_read_outside(workdir: Path) -> None:
    result = run_bash("cat /etc/hostname", workdir)
    assert result.ok


def test_edit_unique(workdir: Path) -> None:
    result = run_edit("a.txt", "alpha", "ALPHA", workdir)
    assert result.ok
    assert run_read("a.txt", workdir).output == "ALPHA\nbeta\n"


def test_edit_not_found(workdir: Path) -> None:
    result = run_edit("a.txt", "nope", "x", workdir)
    assert not result.ok


def test_grep_finds(workdir: Path) -> None:
    result = run_grep("gamma", workdir, ".")
    assert result.ok
    assert "sub/b.txt:1" in result.output


def test_glob_lists(workdir: Path) -> None:
    result = run_glob("**/*.txt", workdir)
    assert "a.txt" in result.output
    assert "sub/b.txt" in result.output


def test_execute_tool_unknown(workdir: Path) -> None:
    result = execute_tool("teleport", {}, workdir)
    assert not result.ok
