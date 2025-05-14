from pathlib import Path
import pandas as pd
from etl.transform.clean import load_and_clean_data
from etl.transform.enrich import enrich_data


# loads the downloaded dataset then runs the cleaning and enrichment functions
def transform_steam_games(raw_csv_path: Path) -> pd.DataFrame:
    raw_csv_path = Path(raw_csv_path)
    clean_csv = raw_csv_path.parent / "steam_games_clean.csv"
    enriched_csv = raw_csv_path.parent / "steam_games_enriched.csv"

    df_clean = load_and_clean_data(raw_csv_path)
    df_clean.to_csv(clean_csv, index=False)

    df_enriched = enrich_data(df_clean)
    df_enriched.to_csv(enriched_csv, index=False)

    return df_enriched


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[2]
    RAW = BASE_DIR / "data" / "games_march2025_full.csv"
    transform_steam_games(RAW)
