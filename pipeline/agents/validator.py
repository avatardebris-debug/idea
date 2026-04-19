"""
pipeline/agents/validator.py
Validator/Tester agent — runs tests, lint, and acceptance checks.

Receives: workspace path + file list after Executor finishes
Produces: validation_report.md, sends result to Reviewer (on PASS) or back to Executor (on FAIL)
"""

from __future__ import annotations

import ast
import logging
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.agent_process import AgentProcess, AgentOutput
from pipeline.message_bus import Message

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Import-name → pip-package-name mapping
# Add entries here whenever a new package is encountered.
# ---------------------------------------------------------------------------
_IMPORT_TO_PIP: dict[str, str | None] = {
    # Web scraping / HTTP
    "bs4": "beautifulsoup4",
    "requests": "requests",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "lxml": "lxml",
    "selenium": "selenium",
    "playwright": "playwright",
    # Data / science
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "statsmodels": "statsmodels",
    # Image / media
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "imageio": "imageio",
    # Config / serialization
    "yaml": "pyyaml",
    "toml": "toml",
    "dotenv": "python-dotenv",
    # PDF / Office
    "fitz": "pymupdf",
    "pypdf": "pypdf",
    "PyPDF2": "PyPDF2",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "openpyxl": "openpyxl",
    # AI / ML
    "openai": "openai",
    "anthropic": "anthropic",
    "tiktoken": "tiktoken",
    "transformers": "transformers",
    "torch": "torch",
    "whisper": "openai-whisper",
    "faster_whisper": "faster-whisper",
    # Video / audio
    "yt_dlp": "yt-dlp",
    "pytube": "pytube",
    "pydub": "pydub",
    "moviepy": "moviepy",
    # Web frameworks
    "flask": "flask",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "django": "django",
    "starlette": "starlette",
    # Databases
    "sqlalchemy": "sqlalchemy",
    "pymongo": "pymongo",
    "redis": "redis",
    "psycopg2": "psycopg2-binary",
    # CLI / output
    "click": "click",
    "rich": "rich",
    "typer": "typer",
    "tqdm": "tqdm",
    # Crypto / auth
    "jwt": "PyJWT",
    "Crypto": "pycryptodome",
    # Misc
    "chardet": "chardet",
    "dateutil": "python-dateutil",
    "pydantic": "pydantic",
    "attr": "attrs",
    "loguru": "loguru",
    "paramiko": "paramiko",
    "serial": "pyserial",
    # stdlib aliases (no install needed)
    "tomllib": None,   # stdlib in Python 3.11+
    "typing_extensions": "typing_extensions",
}

# Modules we know are stdlib — supplement sys.stdlib_module_names for older Pythons
_KNOWN_STDLIB = {
    "abc", "argparse", "ast", "asyncio", "base64", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "email", "enum",
    "functools", "glob", "hashlib", "http", "importlib", "inspect", "io",
    "itertools", "json", "logging", "math", "multiprocessing", "operator",
    "os", "pathlib", "pickle", "platform", "pprint", "queue", "random",
    "re", "shutil", "signal", "socket", "sqlite3", "string", "struct",
    "subprocess", "sys", "tempfile", "textwrap", "threading", "time",
    "traceback", "typing", "unicodedata", "unittest", "urllib", "uuid",
    "warnings", "weakref", "xml", "xmlrpc", "zipfile", "zlib",
    "__future__", "_thread", "builtins",
}


def _stdlib_modules() -> set[str]:
    if hasattr(sys, "stdlib_module_names"):          # Python 3.10+
        return sys.stdlib_module_names | _KNOWN_STDLIB   # type: ignore[operator]
    return _KNOWN_STDLIB


def _collect_imports(workspace: pathlib.Path) -> set[str]:
    """AST-parse all .py files and return top-level module names imported."""
    names: set[str] = set()
    for py in workspace.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names.add(node.module.split(".")[0])
    return names


def auto_install_workspace_deps(workspace: pathlib.Path) -> list[str]:
    """
    Deterministically install every missing dependency for code in `workspace`.

    Steps:
      1. pip install -r requirements.txt  (if present)
      2. pip install from pyproject.toml  (if present and parseable)
      3. AST-scan all .py files → collect imports → try to import each →
         pip install anything that fails.

    Returns a list of packages that were actually installed.
    """
    installed: list[str] = []
    stdlib = _stdlib_modules()

    # --- Step 1: requirements.txt ---
    req = workspace / "requirements.txt"
    if req.exists():
        logger.info("[validator] Installing from requirements.txt")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req), "-q"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            installed.append("(requirements.txt)")
            logger.info("[validator] requirements.txt installed OK")
        else:
            logger.warning("[validator] requirements.txt install failed: %s", r.stderr[:400])

    # --- Step 2: pyproject.toml (best-effort) ---
    pyproject = workspace / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            # Try stdlib tomllib first (Python 3.11+), fall back to toml package
            try:
                import tomllib  # type: ignore
                data = tomllib.loads(content)
            except ImportError:
                try:
                    import toml  # type: ignore
                    data = toml.loads(content)
                except ImportError:
                    data = {}
            deps = (
                data.get("project", {}).get("dependencies", [])
                or data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            )
            if isinstance(deps, dict):
                pkgs = [k for k in deps if k.lower() != "python"]
            else:
                pkgs = [str(d).split(">")[0].split("<")[0].split("=")[0].split("!")[0].strip()
                        for d in deps]
            if pkgs:
                logger.info("[validator] Installing from pyproject.toml: %s", pkgs)
                r = subprocess.run(
                    [sys.executable, "-m", "pip", "install", *pkgs, "-q"],
                    capture_output=True, text=True,
                )
                if r.returncode == 0:
                    installed.extend(pkgs)
        except Exception as e:
            logger.warning("[validator] pyproject.toml parse failed: %s", e)

    # --- Step 3: AST import scan ---
    third_party = _collect_imports(workspace) - stdlib
    for mod in sorted(third_party):
        # Skip if already importable
        try:
            __import__(mod)
            continue
        except ImportError:
            pass
        except Exception:
            continue  # e.g. ModuleNotFoundError with extras

        pip_pkg = _IMPORT_TO_PIP.get(mod, mod)   # default: same name
        if pip_pkg is None:
            continue  # explicitly stdlib alias

        logger.info("[validator] Auto-installing '%s' (import '%s')", pip_pkg, mod)
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_pkg, "-q"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            installed.append(pip_pkg)
        else:
            logger.warning("[validator] Failed to install %s: %s", pip_pkg, r.stderr[:300])

    if installed:
        logger.info("[validator] Deps installed: %s", installed)
    return installed


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class ValidatorAgent(AgentProcess):
    role = "validator"
    max_steps = 20
    temperature = 0.2   # deterministic test running
    think = False       # mechanical validation — no CoT needed

    def handle(self, msg: Message) -> AgentOutput:
        phase_num = msg.payload.get("phase", 1)
        idea_slug = msg.payload.get("idea_slug", self._current_slug)
        workspace_path = msg.payload.get("workspace_path", str(self.get_workspace_path()))
        files_written = msg.payload.get("files_written", [])
        tasks_path = msg.payload.get("tasks_path", f"phases/phase_{phase_num}/tasks.md")
        report_path = msg.payload.get(
            "validation_report_path",
            f"phases/phase_{phase_num}/validation_report.md",
        )
        report_full_path = self._project_path(report_path)

        self._update_idea_status(f"phase_{phase_num}_validating")

        # ------------------------------------------------------------------
        # PRE-VALIDATION: deterministic dependency installation
        # This runs BEFORE the LLM so tests can't fail from missing modules.
        # ------------------------------------------------------------------
        ws = pathlib.Path(workspace_path)
        if ws.exists():
            try:
                auto_install_workspace_deps(ws)
            except Exception as e:
                logger.warning("[validator] auto_install_workspace_deps error: %s", e)

        # Read task list for acceptance criteria
        tasks_content = self.read_state_file(tasks_path)

        task_prompt = (
            f"You are validating Phase {phase_num} code output.\n\n"
            f"## Workspace\n"
            f"All code is in: {workspace_path}\n"
            f"Files written: {', '.join(files_written) if files_written else '(check workspace)'}\n\n"
            f"## Task List (for acceptance criteria)\n{tasks_content}\n\n"
            f"## Your Job\n"
            f"NOTE: All Python dependencies have already been auto-installed before this step.\n"
            f"If a test still fails with ModuleNotFoundError, run `pip install <pkg>` then retry.\n\n"
            f"1. Use `list_tree` on {workspace_path} to see all files.\n"
            f"2. Read each code file.\n"
            f"3. Run tests: `run_shell` with `cd {workspace_path} && python -m pytest -v` "
            f"(if test files exist).\n"
            f"4. Run lint: `run_shell` with `cd {workspace_path} && python -m ruff check .` "
            f"(skip if ruff not installed).\n"
            f"5. Check each acceptance criterion from the task list.\n"
            f"6. Write your validation report to `{report_full_path}`.\n"
            f"7. End with a clear **Verdict: PASS** or **Verdict: FAIL**.\n"
            f"8. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Determine verdict from the structured report ONLY
        report_content = self.read_state_file(report_path)
        is_pass = bool(report_content) and "Verdict: PASS" in report_content

        if is_pass:
            out_msg = Message.create(
                from_agent=self.role,
                to_agent="reviewer",
                type="task",
                payload={
                    "phase": phase_num,
                    "workspace_path": workspace_path,
                    "files_written": files_written,
                    "tasks_path": tasks_path,
                    "validation_report_path": report_path,
                    "review_path": f"phases/phase_{phase_num}/review.md",
                    "idea_slug": idea_slug,
                },
            )
        else:
            retry_count = msg.payload.get("retry_count", 0) + 1
            if retry_count >= 3:
                out_msg = Message.create(
                    from_agent=self.role,
                    to_agent="manager",
                    type="signal",
                    payload={
                        "signal": "PHASE_STUCK",
                        "phase": phase_num,
                        "reason": f"Validation failed after {retry_count} fix attempts",
                        "validation_report": report_content[:2000],
                        "idea_slug": idea_slug,
                    },
                )
            else:
                out_msg = Message.create(
                    from_agent=self.role,
                    to_agent="executor",
                    type="task",
                    payload={
                        "phase": phase_num,
                        "tasks_path": tasks_path,
                        "workspace_path": workspace_path,
                        "fix_required": True,
                        "retry_count": retry_count,
                        "validation_report": report_content[:3000],
                        "error_summary": f"Validation FAILED (attempt {retry_count}/3)",
                        "idea_slug": idea_slug,
                    },
                )

        return AgentOutput(
            success=is_pass,
            answer=result.answer,
            outgoing=[out_msg],
            tokens_used=result.tokens_used,
            steps_used=result.steps_used,
        )


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen3.5:35b")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [validator] %(message)s")

    agent = ValidatorAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
