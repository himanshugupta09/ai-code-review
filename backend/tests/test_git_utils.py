import subprocess

from git_utils import get_repo_diff


def _run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def test_get_repo_diff_detects_added_line(tmp_path):
    _run(["git", "init"], tmp_path)
    _run(["git", "config", "user.email", "test@example.com"], tmp_path)
    _run(["git", "config", "user.name", "Test"], tmp_path)

    file_path = tmp_path / "sample.py"
    file_path.write_text("print('hello')\n")
    _run(["git", "add", "."], tmp_path)
    _run(["git", "commit", "-m", "initial"], tmp_path)

    file_path.write_text("print('hello')\nprint('world')\n")

    files = get_repo_diff(str(tmp_path), base="HEAD")

    assert len(files) == 1
    assert files[0]["path"] == "sample.py"

    added_lines = [
        line["content"]
        for hunk in files[0]["hunks"]
        for line in hunk["lines"]
        if line["line_type"] == "add"
    ]
    assert "print('world')" in added_lines