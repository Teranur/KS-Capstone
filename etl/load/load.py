import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env.dev", override=True)


# DB connection settings
TABLE = "kr_so_capstone"
DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA", "c12de")


def get_engine():
    if not all([DB_USER, DB_HOST, DB_NAME]):
        raise RuntimeError(
            "Missing DB_USER, DB_HOST, or DB_NAME in environment"
        )
    url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PWD}@{DB_HOST}:"
        f"{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(url, echo=True)

    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute(f"SET search_path TO {DB_SCHEMA}")
        cur.close()

    return engine


def load_data_to_postgres(csv_path: Path):
    """
    1) Exec create_tb.sql (drops & creates the table).
    2) Truncate the table.
    3) Bulk-load the CSV via COPY.
    """
    sql_file = PROJECT_ROOT / "sql" / "create_tb.sql"
    table_sql = sql_file.read_text()

    engine = get_engine()
    with engine.begin() as conn:
        # (re)create the table
        conn.execute(text(table_sql))
        # clear out old rows
        conn.execute(text(f"TRUNCATE TABLE {DB_SCHEMA}.{TABLE}"))

    # COPY CSV
    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()
        with open(csv_path, "r", encoding="utf-8") as f:
            cur.copy_expert(
                f"COPY {DB_SCHEMA}.{TABLE} FROM STDIN WITH CSV HEADER", f
            )
        raw_conn.commit()
    finally:
        raw_conn.close()

    print(f"✅ Loaded '{csv_path.name}' into {DB_SCHEMA}.{TABLE}")


if __name__ == "__main__":
    csv_file = PROJECT_ROOT / "data" / "steam_games_enriched.csv"
    load_data_to_postgres(csv_file)
