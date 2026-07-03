import re
import shutil
import stat
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "data").exists() and (candidate / "docs").exists():
            return candidate
    workspace = Path("/workspace")
    if (workspace / "data").exists() and (workspace / "docs").exists():
        return workspace
    return Path(__file__).resolve().parents[3]


REPO_ROOT = _repo_root()


def _tracked_files() -> list[str]:
    if shutil.which("git"):
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.splitlines()

    return [
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "node_modules" not in path.parts
        and ".next" not in path.parts
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
    ]


def test_public_safety_script_is_executable_and_passes() -> None:
    script = REPO_ROOT / "scripts" / "check_public_safety.sh"

    assert script.exists()
    assert script.stat().st_mode & stat.S_IXUSR

    result = subprocess.run(
        ["bash", str(script)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "No high-confidence API key/token pattern found" in result.stdout


def test_no_non_example_env_files_are_tracked() -> None:
    tracked_files = _tracked_files()

    tracked_env_files = [
        line
        for line in tracked_files
        if Path(line).name.startswith(".env") and Path(line).name != ".env.example"
    ]

    assert tracked_env_files == []


def test_public_docs_and_data_do_not_contain_high_confidence_secret_patterns() -> None:
    pattern = re.compile(
        r"(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|"
        r"ghp_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})"
    )

    scan_prefixes = ("README.md", "docs/", "data/", "scripts/", "frontend/", "backend/app/")

    for relative_path in _tracked_files():
        if relative_path.startswith(scan_prefixes):
            path = REPO_ROOT / relative_path
            assert not pattern.search(path.read_text(encoding="utf-8", errors="ignore")), path
