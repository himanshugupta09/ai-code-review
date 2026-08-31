from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from git_utils import get_repo_diff
from static_analysis import run_static_analysis

app = FastAPI(title="AI Code Review Backend", version="0.1.0")

# Electron loads the UI from localhost/file:// — tighten this once the
# desktop shell's actual origin is known.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class LintRequest(BaseModel):
    repo_path: str
    files: list[str]


class DiffRequest(BaseModel):
    repo_path: str
    base: str = "HEAD"


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-code-review-backend"}


@app.post("/diff")
def read_diff(request: DiffRequest):
    try:
        return {"files": get_repo_diff(request.repo_path, request.base)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/lint")
def lint_files(request: LintRequest):
    try:
        return {"findings": run_static_analysis(request.files, request.repo_path)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
