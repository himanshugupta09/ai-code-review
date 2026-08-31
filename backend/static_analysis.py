import json
import subprocess
from collections import defaultdict
from pathlib import Path

PYLINT_SEVERITY_MAP = {
    "error": "bug",
    "fatal": "bug",
    "warning": "style",
    "refactor": "performance",
    "convention": "style",
}


def run_pylint(file_paths: list[str], repo_path: str) -> list[dict]:
    result = subprocess.run(
        ["pylint", "--output-format=json", *file_paths],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    try:
        raw_findings = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []

    return [
        {
            "file_path": item["path"],
            "line_number": item.get("line"),
            "severity": PYLINT_SEVERITY_MAP.get(item.get("type", "convention"), "style"),
            "message": item.get("message", ""),
            "source": "linter",
        }
        for item in raw_findings
    ]


def run_eslint(file_paths: list[str], repo_path: str) -> list[dict]:
    result = subprocess.run(
        ["npx", "--yes", "eslint", "--format=json", *file_paths],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    try:
        raw_files = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []

    findings = []
    for file_result in raw_files:
        for msg in file_result.get("messages", []):
            findings.append(
                {
                    "file_path": file_result.get("filePath", ""),
                    "line_number": msg.get("line"),
                    "severity": "bug" if msg.get("severity") == 2 else "style",
                    "message": msg.get("message", ""),
                    "source": "linter",
                }
            )
    return findings


LINTER_REGISTRY = {
    ".py": run_pylint,
    ".js": run_eslint,
    ".jsx": run_eslint,
    ".ts": run_eslint,
    ".tsx": run_eslint,
}


def run_static_analysis(file_paths: list[str], repo_path: str) -> list[dict]:
    """Group files by extension and run each through its registered linter.
    Files with no registered linter are silently skipped (not an error) —
    the AI review still covers them even without static analysis.
    """
    by_extension = defaultdict(list)
    for f in file_paths:
        by_extension[Path(f).suffix].append(f)

    findings = []
    for ext, files in by_extension.items():
        linter_fn = LINTER_REGISTRY.get(ext)
        if linter_fn:
            findings.extend(linter_fn(files, repo_path))
    return findings