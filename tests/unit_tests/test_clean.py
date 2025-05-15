# The following function was generated with the assistance of ChatGPT.

import pandas as pd
import pytest
from pathlib import Path
from etl.transform.clean import (
    load_data,
    drop_unnecessary_columns,
    clean_numerical_columns,
    clean_categorical_columns,
    owner_to_numeric,
)


# owner_to_numeric
def test_owner_to_numeric_valid():
    assert owner_to_numeric("10-20") == 15
    assert owner_to_numeric("0-0") == 0


def test_owner_to_numeric_invalid():
    assert owner_to_numeric("foo-bar") is None
    assert owner_to_numeric("") is None
    assert owner_to_numeric(None) is None


# drop_unnecessary_columns
def test_drop_unnecessary_columns():
    data = {
        'appid': [1, 2, 2],
        'name': ["A", "B", "B"],
        'release_date': ["2020-01-01", "2021-02-02", "2021-02-02"],
        'price': [0, 5, 5],
        'dlc_count': [0, 1, 1],
        'header_image': ["u1", "u2", "u2"],
        'about_the_game': ["d1", "d2", "d2"],
        'windows': [True, False, False],
        'mac': [False, True, True],
        'linux': [False, False, False],
        'metacritic_score': [0, 80, 80],
        'recommendations': [10, 20, 20],
        'developers': ["X", "Y", "Y"],
        'categories': ["['C1']", "['C2']", "['C2']"],
        'genres': ["['G1']", "['G2']", "['G2']"],
        'positive': [5, 10, 10],
        'negative': [1, 2, 2],
        'estimated_owners': ["0-10", "100-200", "100-200"],
        'peak_ccu': [100, 200, 200],
        'extra': ['x', 'y', 'y']
    }
    df = pd.DataFrame(data)
    out = drop_unnecessary_columns(df)

    expected_cols = {
        'appid', 'name', 'release_date', 'price', 'dlc_count', 'header_image',
        'about_the_game', 'windows', 'mac', 'linux', 'metacritic_score',
        'recommendations', 'developers', 'categories', 'genres', 'positive',
        'negative', 'estimated_owners', 'current_players'
    }
    assert set(out.columns) == expected_cols
    # duplicates by 'name' dropped
    assert out['name'].tolist() == ["A", "B"]


# clean_numerical_columns
def test_clean_numerical_columns():
    df = pd.DataFrame({
        'price': [0, 10, 20],
        'estimated_owners': ["0-100", "50-150", "bad"]
    })
    out = clean_numerical_columns(df.copy())

    # price 0 → 'Free', others unchanged
    assert out.loc[0, 'price'] == 0
    assert out.loc[1, 'price'] == 10
    assert out.loc[2, 'price'] == 20

    # estimated_owners mid-point or None
    assert out.loc[0, 'estimated_owners'] == 50
    assert out.loc[1, 'estimated_owners'] == 100
    assert pd.isna(out.loc[2, 'estimated_owners'])
    
    
# clean_categorical_columns
def test_clean_categorical_columns():
    df = pd.DataFrame({
        'name': ["Game", "Playtest Title", None],
        'about_the_game': [None, "desc", None]
    })
    out = clean_categorical_columns(df.copy())

    # missing names dropped
    assert df.shape[0] > out.shape[0]
    assert not out['name'].isna().any()

    # any title containing "playtest" dropped
    assert not any("playtest" in n.lower() for n in out['name'])

    # missing descriptions filled
    assert all(
        desc == "No description available"
        for desc in out['about_the_game']
    )


# load_data
def test_load_data_parses_dates(tmp_path):
    # write a small CSV with one good and one bad date
    csv = tmp_path / "test.csv"
    csv.write_text("appid,release_date\n1,2020-01-01\n2,bad\n")
    df = load_data(str(csv))

    assert pd.api.types.is_datetime64_any_dtype(df['release_date'])
    assert df.loc[0, 'release_date'].year == 2020
    assert pd.isna(df.loc[1, 'release_date'])
