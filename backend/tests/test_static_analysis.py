from static_analysis import LINTER_REGISTRY, run_pylint, run_static_analysis


def test_run_pylint_flags_unused_import(tmp_path):
    file_path = tmp_path / "bad.py"
    file_path.write_text("import os\n\n\ndef foo():\n    return 1\n")

    findings = run_pylint(["bad.py"], str(tmp_path))

    assert len(findings) > 0
    assert all(f["source"] == "linter" for f in findings)


def test_run_static_analysis_dispatches_by_extension(monkeypatch, tmp_path):
    calls = {}

    def fake_python_linter(files, repo_path):
        calls["python"] = files
        return [{"file_path": files[0], "source": "linter"}]

    def fake_js_linter(files, repo_path):
        calls["js"] = files
        return []

    monkeypatch.setitem(LINTER_REGISTRY, ".py", fake_python_linter)
    monkeypatch.setitem(LINTER_REGISTRY, ".js", fake_js_linter)

    findings = run_static_analysis(["a.py", "b.js"], str(tmp_path))

    assert calls["python"] == ["a.py"]
    assert calls["js"] == ["b.js"]
    assert len(findings) == 1