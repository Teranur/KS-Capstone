import os
import sys
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi

# Set up paths
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_raw"))
os.makedirs(output_dir, exist_ok=True)
#  read the dataset_id and csv_filename from kaggle
dataset_id = "artermiloff/steam-games-dataset"
csv_filename = "games_march2025_full.csv"
# where to download the dataset
csv_path = os.path.join(output_dir, csv_filename)


def extract_steam_data():
    try:
        #  Autheticate Kaggle API, you need to have kaggle.json in ~/.kaggle
        print("Authenticating Kaggle API...")
        api = KaggleApi()
        api.authenticate()
        #  Download the dataset from Kaggle
        print("Downloading CSV file from Kaggle...")
        api.dataset_download_file(
            dataset=dataset_id,
            file_name=csv_filename,
            path=output_dir,
            force=True
        )
        #  checks if the file is downloaded
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
        # loads the csv file into a pandas dataframe to check if the download was successful
        print("Loading CSV file...")
        df = pd.read_csv(csv_path, encoding="ISO-8859-1")
        # preview of the data
        print("Data extraction successful. Preview:")
        print(df.head(5))

    except Exception as e:
        print(f"Error during data extraction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    extract_steam_data()
