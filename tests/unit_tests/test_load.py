import pytest
from pathlib import Path
from unittest.mock import MagicMock, call

import etl.load.load as load_mod

# The table name your loader writes into
TABLE = "kr_so_capstone"


@pytest.fixture
def dummy_sql_dir(tmp_path):
    """
    Create a fake project structure with:
      - project_root/sql/create_schema.sql
      - project_root/sql/create_tb.sql
      - data/steam_games_enriched.csv
    """
    project_root = tmp_path / "project_root"
    sql_dir = project_root / "sql"
    data_dir = tmp_path / "data"
    sql_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    # Create minimal SQL files
    schema_sql = sql_dir / "create_schema.sql"
    schema_sql.write_text("CREATE SCHEMA IF NOT EXISTS df_capstone;")
    table_sql = sql_dir / "create_tb.sql"
    table_sql.write_text("DROP TABLE IF EXISTS df_capstone.kr_so_capstone;\n"
                         "CREATE TABLE df_capstone.kr_so_capstone (...);")

    # Create a dummy CSV
    dummy_csv = data_dir / "steam_games_enriched.csv"
    dummy_csv.write_text("appid,name\n")  # just a header, loader won't actually read here

    return {
        "project_root": project_root,
        "schema_sql": schema_sql,
        "table_sql": table_sql,
        "dummy_csv": dummy_csv,
    }


def test_load_data_to_postgres_executes(dummy_sql_dir, monkeypatch):
    project_root = dummy_sql_dir["project_root"]
    csv_path = dummy_sql_dir["dummy_csv"]

    # Create a fake Engine with .begin() context manager
    fake_conn = MagicMock()
    fake_begin = MagicMock()
    fake_begin.__enter__.return_value = fake_conn
    fake_begin.__exit__.return_value = False

    fake_engine = MagicMock()
    fake_engine.begin.return_value = fake_begin

    # Fake raw_connection and cursor
    fake_raw = MagicMock()
    fake_cursor = MagicMock()
    fake_raw.cursor.return_value = fake_cursor
    fake_engine.raw_connection.return_value = fake_raw

    # Patch get_engine() in your loader module
    monkeypatch.setattr(load_mod, "get_engine", lambda: fake_engine)

    # Run the loader
    load_mod.load_data_to_postgres(Path(csv_path))

    # 1) Verify DDL statements were executed
    #    We inspect the `.text` attribute of each TextClause passed to `execute()`.
    executed_sql = [c.args[0].text for c in fake_conn.execute.call_args_list]

    assert any("CREATE TABLE" in sql for sql in executed_sql), \
        "Expected a CREATE TABLE statement"
    assert any(f"TRUNCATE TABLE {TABLE}" in sql for sql in executed_sql), \
        "Expected a TRUNCATE TABLE statement"

    # 2) Verify COPY was called on the psycopg cursor
    fake_cursor.copy_expert.assert_called_once()
