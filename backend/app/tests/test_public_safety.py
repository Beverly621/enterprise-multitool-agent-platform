import re
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


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
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    tracked_env_files = [
        line
        for line in result.stdout.splitlines()
        if Path(line).name.startswith(".env") and Path(line).name != ".env.example"
    ]

    assert tracked_env_files == []


def test_public_docs_and_data_do_not_contain_high_confidence_secret_patterns() -> None:
    pattern = re.compile(
        r"(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|"
        r"ghp_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})"
    )

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    scan_prefixes = ("README.md", "docs/", "data/", "scripts/", "frontend/", "backend/app/")
    for relative_path in result.stdout.splitlines():
        if relative_path.startswith(scan_prefixes):
            path = REPO_ROOT / relative_path
            assert not pattern.search(path.read_text(encoding="utf-8", errors="ignore")), path
