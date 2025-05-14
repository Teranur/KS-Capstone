import ast
import pandas as pd
import time
from pathlib import Path


# loads the downloaded dataset
#  and converts the release_date column to datetime
def load_data(filepath):
    df = pd.read_csv(filepath)
    df = df.copy()
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    return df


# keeps only the necessary columns for analysis
# renames the peak_ccu column to current_players
# drops duplicates from the name column and the dataframe
def drop_unnecessary_columns(df):
    columns_for_analysis = [
        'appid', 'name', 'release_date', 'price', 'dlc_count',
        'header_image', 'about_the_game', 'windows', 'mac', 'linux',
        'metacritic_score', 'recommendations', 'developers', 'categories',
        'genres', 'positive', 'negative', 'estimated_owners', 'peak_ccu'
    ]
    df = df[columns_for_analysis].copy()
    df.rename(columns={"peak_ccu": "current_players"}, inplace=True)
    df.drop_duplicates(inplace=True)
    df.drop_duplicates(subset=['name'], keep='first', inplace=True)
    return df


# converts estimated owners from a string range to numeric avg
def clean_numerical_columns(df):
    df['estimated_owners'] = df['estimated_owners'].apply(owner_to_numeric)
    return df


# drops games with missing names
# drops playtest games
# fills missing descriptions with a default message
def clean_categorical_columns(df):
    df = df.dropna(subset=['name'])
    mask = df['name'].str.contains("playtest", case=False, na=False)
    df = df.loc[~mask].copy()
    df['about_the_game'] = df['about_the_game'].fillna('No description available')
    return df


# removes duplicates from the categories and genres columns
# makes it consistent format
def normalize_list_columns(df):
    for col in ('categories', 'genres'):
        def normalize(cell):
            if isinstance(cell, str):
                try:
                    items = ast.literal_eval(cell)
                    if isinstance(items, (list, tuple)):
                        unique = sorted({str(x).strip() for x in items})
                        return ",".join(unique)
                except Exception:
                    # fallback: split on commas, strip brackets/quotes
                    parts = [p.strip(" []'\"") for p in cell.split(',')]
                    unique = sorted({p for p in parts if p})
                    return ",".join(unique)
            return cell
        df[col] = df[col].fillna("").apply(normalize)
    return df


# function to convert estimated owners from a string range to numeric avg
def owner_to_numeric(value):
    try:
        low, high = value.split('-')
        return (int(low) + int(high)) // 2
    except Exception:
        return None
    
    
# runs the above functions in order
def load_and_clean_data(filepath):
    df = load_data(filepath)
    df = drop_unnecessary_columns(df)
    df = clean_numerical_columns(df)
    df = clean_categorical_columns(df)
    df = normalize_list_columns(df)
    # saves the cleaned dataset to a new CSV file
    output_path = Path('data') / 'steam_games_clean.csv'
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to {output_path}")
    return df


if __name__ == '__main__':
    start = time.perf_counter()
    raw_csv = Path('data') / 'games_march2025_full.csv'
    df = load_and_clean_data(raw_csv)
    elapsed = time.perf_counter() - start
    print(f"Transform (clean) completed in {elapsed:.2f} seconds.")
