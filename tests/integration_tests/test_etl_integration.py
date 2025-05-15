import pandas as pd
import pytest
from pathlib import Path
from sqlalchemy import create_engine, text

from etl.transform.transform import transform_steam_games
import etl.load.load as load_mod


@pytest.fixture
def tmp_data_dir(tmp_path_factory):
    """
    Create a temporary `data/` folder containing a minimal
    `games_march2025_full.csv` for the pipeline to ingest.
    """
    data_dir = tmp_path_factory.mktemp("data")
    raw_csv = data_dir / "games_march2025_full.csv"

    df = pd.DataFrame({
        "appid": [1, 2],
        "name": ["Game A", "Game B"],
        "release_date": ["2023-01-01", "2024-02-02"],
        "price": [0, 10],
        "dlc_count": [0, 1],
        "header_image": ["", ""],
        "about_the_game": ["Desc A", "Desc B"],
        "windows": [True, False],
        "mac": [False, True],
        "linux": [False, False],
        "metacritic_score": [50, 80],
        "recommendations": [5, 10],
        "developers": ["DevA", "DevB"],
        "categories": ['["Action"]', '["Indie"]'],
        "genres": ['["RPG"]', '["Puzzle"]'],
        "positive": [10, 20],
        "negative": [2, 5],
        "estimated_owners": ["100-200", "50-150"],
        "peak_ccu": [0, 0],
    })
    df.to_csv(raw_csv, index=False)
    return data_dir


@pytest.fixture
def sqlite_engine():
    """
    Create an in-memory SQLite engine and monkey-patch load_data_to_postgres
    so it writes into SQLite instead of Postgres.
    """
    engine = create_engine("sqlite:///:memory:")

    def load_sqlite(csv_path: Path):
        # 1) Read enriched data
        df = pd.read_csv(csv_path)

        # 2) Create table schema
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS kr_so_capstone (
                    appid INTEGER PRIMARY KEY,
                    name TEXT,
                    release_date DATE,
                    price TEXT,
                    dlc_count INTEGER,
                    header_image TEXT,
                    about_the_game TEXT,
                    windows BOOLEAN,
                    mac BOOLEAN,
                    linux BOOLEAN,
                    metacritic_score INTEGER,
                    recommendations INTEGER,
                    developers TEXT,
                    categories TEXT,
                    genres TEXT,
                    positive INTEGER,
                    negative INTEGER,
                    estimated_owners INTEGER,
                    current_players INTEGER,
                    release_year INTEGER,
                    estimated_revenue REAL,
                    price_tier TEXT,
                    positive_ratio REAL
                )
            """))

        # 3) Bulk insert via pandas
        df.to_sql("kr_so_capstone", engine, if_exists="replace", index=False)

    # Override the real loader
    load_mod.load_data_to_postgres = load_sqlite

    return engine


def test_full_pipeline(tmp_data_dir, sqlite_engine):
    """
    Run the full ETL: extract (skipped, we already have CSV),
    transform → enriched CSV, then load into SQLite.
    Finally verify table contents.
    """
    data_dir = tmp_data_dir
    raw_csv = data_dir / "games_march2025_full.csv"
    enriched_csv = data_dir / "steam_games_enriched.csv"

    # Transform step
    df_enriched = transform_steam_games(raw_csv)
    assert enriched_csv.exists()
    # Sanity check on enrichment
    assert "current_players" in df_enriched.columns
    assert "positive_ratio" in df_enriched.columns

    # Load into our SQLite
    load_mod.load_data_to_postgres(enriched_csv)

    # Verify via SQLAlchemy
    with sqlite_engine.connect() as conn:
        # row count
        count = conn.execute(text("SELECT COUNT(*) FROM kr_so_capstone")).scalar()
        assert count == 2

        # check one record’s metrics
        row = conn.execute(
            text("SELECT name, positive_ratio FROM kr_so_capstone WHERE appid=1")
        ).mappings().one()
        assert row["name"] == "Game A"
        # positive_ratio = 10/(10+2)*100 ≈ 83.3
        assert pytest.approx(row["positive_ratio"], rel=1e-2) == 10 / (10 + 2) * 100
