import os
import time
from kaggle.api.kaggle_api_extended import KaggleApi

# Set up paths
output_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
os.makedirs(output_dir, exist_ok=True)
#  identifies the dataset to download
dataset_id = "artermiloff/steam-games-dataset"
csv_filename = "games_march2025_full.csv"
# where to download the dataset
csv_path = os.path.join(output_dir, csv_filename)


# function to extract the steam dataset from Kaggle
#  and load it into a pandas dataframe
def extract_steam_data():
    try:
        #  Autheticate Kaggle API, you need to have kaggle.json in ~/.kaggle
        print("Authenticating Kaggle API...")
        api = KaggleApi()
        api.authenticate()
        #  Download the dataset from Kaggle
        api.dataset_download_file(
            dataset=dataset_id,
            file_name=csv_filename,
            path=output_dir,
            force=True
        )
        #  checks if the file is downloaded
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
    except Exception as e:
        print(f"Error during data extraction: {e}")


if __name__ == "__main__":
    start = time.perf_counter()
    extract_steam_data()
    elapsed = time.perf_counter() - start
    print(f"Extraction completed in {elapsed:.2f} seconds.")
