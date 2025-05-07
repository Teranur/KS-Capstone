import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import sys


# This script extracts data from a Kaggle dataset and saves it to a CSV file.
def extract_steam_data():
    file_path = "93182_steam_games.csv" # CSV file name
    dataset_id = "joebeachcapital/top-1000-steam-games" # Kaggle dataset ID

    try:
        print("Starting data extraction from Kaggle...")
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            dataset_id,
            file_path,
        )
        print("Data extraction successful. Previewing 5 records:")
        print(df.head(5))

    except Exception as e:
        print(f"Error during data extraction: {e}")
        sys.exit(1)  # Exit the program with error code 1


if __name__ == "__main__":
    extract_steam_data()
    