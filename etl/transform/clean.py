import pandas as pd


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
    df.drop_duplicates(inplace=True)
    return df


def clean_numerical_columns(df):
    """Clean numerical columns by filling missing values."""
    df['price'] = df['price'].apply(lambda x: 'Free' if x == 0 else x)
    df['metacritic_score'] = df['metacritic_score'].apply(lambda x: 'Not Rated' if x == 0 else x)
    df['estimated_owners'] = df['estimated_owners'].apply(owner_to_numeric)
    return df


def clean_categorical_columns(df):
    """Clean categorical columns by filling or dropping missing values."""
    df['name'] = df['name'].dropna('')
    df['about_the_game'] = df['about_the_game'].fillna('No description available')
    return df


def load_and_clean_data(filepath):
    """Load and clean the steam_games dataset."""
    df = load_data(filepath)
    df = drop_unnecessary_columns(df)
    df = clean_numerical_columns(df)
    df = clean_categorical_columns(df)
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
    df = load_and_clean_data('data_raw/games_march2025_full.csv')