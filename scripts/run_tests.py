# The following function was generated with the assistance of ChatGPT.
from config import setup_env
import os
import sys
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Map commands → test folders and coverage targets
TEST_CONFIG = {
    "unit": {
        "dir": "tests/unit_tests",
        "cov": ["etl.transform.clean", "etl.transform.enrich"],
    },
    "integration": {
        "dir": "tests/integration_tests",
        "cov": ["etl_integration"],
    },
    "component": {
        "dir": "tests/component_tests",
        "cov": ["streamlit"],
    },
    "all": {
        "dir": "tests",
        "cov": ["etl", "streamlit"],
    },
}


def run_python_linting():
    """Run flake8 across the project root."""
    return subprocess.run(["flake8", "."], capture_output=True, text=True)


def run_sql_linting():
    """Run sqlfluff against etl/sql/."""
    sql_dir = os.path.join(PROJECT_ROOT, "sql")
    files = [f for f in os.listdir(sql_dir) if f.endswith(".sql")]
    if not files:
        print(f"No SQL files found in {sql_dir}, skipping SQL lint.")
        return subprocess.CompletedProcess(args=[], returncode=0)
    return subprocess.run(
        ["sqlfluff", "lint", sql_dir], capture_output=True, text=True
    )


def report_lint(name, result):
    if result.returncode == 0:
        print(f"{name} lint passed")
    else:
        print(f"{name} lint FAILED")
        print(result.stdout, result.stderr)


def run_linting():
    print("Python linting…")
    py = run_python_linting()
    report_lint("Python", py)

    print("SQL linting…")
    sql = run_sql_linting()
    report_lint("SQL", sql)


def get_cov_command(cmd):
    cfg = TEST_CONFIG[cmd]
    test_dir = cfg["dir"]
    sources  = ",".join(cfg["cov"])
    # coverage settings (omit patterns, fail thresholds) go in .coveragerc
    return f"coverage run -m pytest --verbose {test_dir} && coverage report -m"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Load test environment
    setup_env(["run_tests", "test"])

    cmd = sys.argv[1]

    if cmd == "lint":
        run_linting()
        return

    if cmd not in TEST_CONFIG:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

    # Run pytest with coverage
    print(f"Running {cmd} tests with coverage…")
    rc = subprocess.call(get_cov_command(cmd), shell=True)
    if rc != 0:
        sys.exit(rc)

    # Then lint everything
    run_linting()


if __name__ == "__main__":
    from pathlib import Path
    main()
