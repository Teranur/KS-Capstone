import pandas as pd
import time


def load_data(filepath):
    """Load the dataset from a CSV file."""
    print(filepath)
    df = pd.read_csv(filepath)
    return df


def drop_unnecessary_columns(df):
    """Drop unnecessary columns and duplicates."""
    columns_for_analysis = [
        'appid', 'name', 'release_date', 'price', 'dlc_count',
        'header_image', 'about_the_game', 'windows', 'mac', 'linux',
        'metacritic_score', 'recommendations', 'developers', 'categories',
        'genres', 'positive', 'negative', 'estimated_owners', 'peak_ccu'
    ]
    df = df[columns_for_analysis].copy()
    #  peak_ccu is the current players upon analysis
    df.rename(columns={"peak_ccu": "current_players"}, inplace=True)
    df.drop_duplicates(inplace=True)
    # duplicates remain in the name column so have to do it again
    df.drop_duplicates(subset=['name'], keep='first', inplace=True)
    return df


def clean_numerical_columns(df):
    """Clean numerical columns by filling missing values."""
    # change 0 to free and still keep the rest of integers
    df['price'] = df['price'].apply(lambda x: 'Free' if x == 0 else x)
    #  same as the above but for 0 change to Not Rated
    df['metacritic_score'] = df['metacritic_score'].apply(lambda x: 'Not Rated' if x == 0 else x) 
    #  changes the string range to an average and changes it to an integer
    df['estimated_owners'] = df['estimated_owners'].apply(owner_to_numeric)
    return df


def clean_categorical_columns(df):
    """Clean categorical columns by filling or dropping missing values."""
    # drop rows with missing names
    df['name'] = df['name'].dropna()
    # filter playtest of games
    mask = df['name'].str.contains("playtest", case=False, na=False)
    # keep records that are not playtest
    df = df[mask == False]
    # fill missing descriptions with a placeholder
    df['about_the_game'] = df['about_the_game'].fillna('No description available')
    return df


def load_and_clean_data(filepath):
    """Load and clean the steam_games dataset."""
    df = load_data(filepath)
    df = drop_unnecessary_columns(df)
    df = clean_numerical_columns(df)
    df = clean_categorical_columns(df)
    #  save the cleaned dataset to a new CSV file
    output_path = "data/steam_games_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to {output_path}")
    return df


#def count_nulls(df):
    null_counts = df.isnull().sum()
    print(null_counts[null_counts > 0])
    
    
def owner_to_numeric(value):
    try:
        low, high = value.split('-')
        numeric_est = (int(low) + int(high)) // 2
        return numeric_est
    except ValueError:
        return None


if __name__ == '__main__':
    start = time.perf_counter()
    df = load_and_clean_data('data/games_march2025_full.csv')
    elapsed = time.perf_counter() - start
    print(f"Transform (clean + enrich) completed in {elapsed:.2f} seconds.")