from git import Repo
from unidiff import PatchSet


def get_repo_diff(repo_path: str, base: str = "HEAD"):
    """Return the working-tree diff against `base` as structured data."""
    repo = Repo(repo_path)
    diff_text = repo.git.diff(base, unified=3)
    patch_set = PatchSet(diff_text)

    files = []
    for patched_file in patch_set:
        hunks = []
        for hunk in patched_file:
            lines = [
                {
                    "line_type": "add"
                    if line.is_added
                    else "remove"
                    if line.is_removed
                    else "context",
                    "content": line.value.rstrip("\n"),
                    "target_line_no": line.target_line_no,
                    "source_line_no": line.source_line_no,
                }
                for line in hunk
            ]
            hunks.append({"section_header": hunk.section_header, "lines": lines})

        files.append(
            {
                "path": patched_file.path,
                "is_added_file": patched_file.is_added_file,
                "is_removed_file": patched_file.is_removed_file,
                "hunks": hunks,
            }
        )

    return files
