import os


class DatabaseConfigError(Exception):
    """Raised when any required DB config is missing or invalid."""


def load_db_config() -> dict[str, str]:
    """
    Reads DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT from environment
    and returns a dict with those values. Raises DatabaseConfigError
    if any required var is unset or empty (except DB_PASSWORD).
    """
    def _get(key: str, default: str | None = None) -> str:
        val = os.getenv(key)
        if val:
            return val
        if default is not None:
            return default
        raise DatabaseConfigError(f"Missing env var: {key}")

    return {
        "dbname":   _get("DB_NAME"),
        "user":     _get("DB_USER"),
        "password": _get("DB_PASSWORD"),
        "host":     _get("DB_HOST"),
        "port":     _get("DB_PORT", "5432"),
    }
