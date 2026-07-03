from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_github_actions_workflows_exist() -> None:
    workflow_dir = ROOT / ".github" / "workflows"

    assert (workflow_dir / "backend-ci.yml").exists()
    assert (workflow_dir / "frontend-ci.yml").exists()
    assert (workflow_dir / "docker-build.yml").exists()
    assert (workflow_dir / "public-safety.yml").exists()


def test_deployment_config_files_exist() -> None:
    assert (ROOT / "deploy" / "docker-compose.prod.yml").exists()
    assert (ROOT / "deploy" / "nginx.conf").exists()
    assert (ROOT / "backend" / ".dockerignore").exists()
    assert (ROOT / "frontend" / ".dockerignore").exists()


def test_deployment_scripts_exist() -> None:
    assert (ROOT / "scripts" / "check_env.sh").exists()
    assert (ROOT / "scripts" / "pre_deploy_check.sh").exists()
    assert (ROOT / "scripts" / "docker_smoke_test.sh").exists()
    assert (ROOT / "backend" / "scripts" / "prestart.sh").exists()
