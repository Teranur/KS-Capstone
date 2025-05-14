import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from etl.extract.extract import extract_steam_data
from etl.transform.transform import transform_steam_games
from etl.load.load import load_data_to_postgres

# sets up the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Check if the script is run with the correct argument
if len(sys.argv) != 2 or sys.argv[1] not in ("dev", "test"):
    raise ValueError("Usage: run_etl [dev|test]")


# Load the appropriate .env file based on the argument
env_file = PROJECT_ROOT / f".env.{sys.argv[1]}"
load_dotenv(env_file, override=True)
print(f"→ Loaded environment from {env_file.name}")


# gets the data for the ETL pipeline
def main():
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_CSV = DATA_DIR / "games_march2025_full.csv"
    ENRICHED_CSV = DATA_DIR / "steam_games_enriched.csv"
# start timer
    total_start = time.perf_counter()
# starts the extraction
    print("▶︎ Extracting raw data from Kaggle…")
    t0 = time.perf_counter()
    extract_steam_data()
    print(f"✔ Extraction completed in {time.perf_counter() - t0:.2f}s\n")
# starts the transformation
    print("▶︎ Cleaning & enriching data…")
    t0 = time.perf_counter()
    transform_steam_games(RAW_CSV)
    print(f"✔ Transform completed in {time.perf_counter() - t0:.2f}s\n")
# loads the cleaned and enriched data into pagila
    print("▶︎ Loading enriched data into database…")
    t0 = time.perf_counter()
    load_data_to_postgres(ENRICHED_CSV)
    print(f"✔ Load completed in {time.perf_counter() - t0:.2f}s\n")
# total Pipeline time
    elapsed = time.perf_counter() - total_start
    print(f"Total ETL pipeline time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
