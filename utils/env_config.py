import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

#: Supported environments
ENVS = ("dev", "test")


def setup_env(argv: list[str]) -> None:
    """
    Load the appropriate .env file based on argv[1]. Example:

        python scripts/run_etl.py dev

    Looks for:
      • .env.dev   when env=='dev'
      • .env.test  when env=='test'

    Clears any previous DB_* vars before loading.
    Raises ValueError if you don’t pass exactly one of ENVS.
    """
    if len(argv) != 2 or argv[1] not in ENVS:
        raise ValueError(f"First argument must be one of {ENVS}, e.g. `run_etl dev`")
    env = argv[1]

    _cleanup_previous_env()

    env_file = f".env.{env}"
    env_path = find_dotenv(
        str(Path.cwd() / env_file),
        raise_error_if_not_found=True,
    )

    load_dotenv(env_path, override=True)
    os.environ["ENV"] = env
    print(f"→ Loaded environment variables from {env_file}")


def _cleanup_previous_env() -> None:
    """
    Remove any lingering DB_* env vars so that load_dotenv(override=True)
    always works cleanly when switching between dev/test.
    """
    for key in ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "STEAM_API_KEY"):
        os.environ.pop(key, None)
