# The following function was generated with the assistance of ChatGPT.

import os
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import MagicMock

import etl.transform.enrich as enrich


@pytest.fixture(autouse=True)
def temp_cache_dir(tmp_path, monkeypatch):
    """
    Redirect the CACHE_PATH in enrich.py to a temp folder so
    tests don’t collide with real data.
    """
    fake_cache = tmp_path / "steam_players_cache.csv"
    monkeypatch.setattr(enrich, "CACHE_PATH", fake_cache)
    return tmp_path


def test_enrich_dates_adds_year_and_renames():
    df = pd.DataFrame({
        "release_date": ["2021-03-15", "bad-date"],
        "peak_ccu": [10, 20],
    })
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    out = enrich.enrich_dates(df.copy())
    # peak_ccu renamed
    assert "current_players" in out.columns and "peak_ccu" not in out.columns
    # dates parsed, year extracted
    assert pd.api.types.is_datetime64_any_dtype(out["release_date"])
    assert out.loc[0, "release_year"] == 2021
    assert pd.isna(out.loc[1, "release_year"])


def test_enrich_price_computes_revenue_and_tiers():
    df = pd.DataFrame({
        "price": ["0", "30", "50"],
        "estimated_owners": [100, 10, 1],
    })
    out = enrich.enrich_price(df.copy())

    # estimated_revenue = owners * price * 0.7
    assert out.loc[0, "estimated_revenue"] == pytest.approx(100 * 0 * 0.7, 0.1)
    assert out.loc[1, "estimated_revenue"] == pytest.approx(10 * 30 * 0.7, 0.1)
    assert out.loc[2, "estimated_revenue"] == pytest.approx(1 * 50 * 0.7, 0.1)

    # price tiers
    assert out.loc[0, "price_tier"] == "Free"
    assert out.loc[1, "price_tier"] == "Standard"
    assert out.loc[2, "price_tier"] == "Premium"

    # helper column dropped
    assert "price_numeric" not in out.columns


def test_enrich_metrics_ratios():
    df = pd.DataFrame({
        "positive": [8, 1],
        "negative": [2, 3],
    })
    out = enrich.enrich_metrics(df.copy())
    # positive_ratio = pos/(pos+neg)*100
    assert out.loc[0, "positive_ratio"] == pytest.approx(8 / 10 * 100, 0.1)
    assert out.loc[1, "positive_ratio"] == pytest.approx(1 / 4 * 100, 0.1)


def test_update_current_players_with_cache_and_api(tmp_path, monkeypatch):
    # Prepare a DF with two appids: one in cache, one new
    df = pd.DataFrame({
        "appid": [1, 2],
        "current_players": [0, 0],
    })

    # Create a fake cache CSV containing only appid=1
    cache_df = pd.DataFrame({"appid": [1], "current_players": [111]})
    cache_path = enrich.CACHE_PATH
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_df.to_csv(cache_path, index=False)

    # Stub fetch_current_players: return 222 for appid=2
    monkeypatch.setattr(enrich, "fetch_current_players", lambda aid: 222)

    out = enrich.update_current_players(df.copy())

    # Appid=1 should get cached value 111, appid=2 gets API value 222
    assert out.loc[out["appid"] == 1, "current_players"].iloc[0] == 111
    assert out.loc[out["appid"] == 2, "current_players"].iloc[0] == 222

    # Also verify the cache file was updated to include appid=2
    new_cache = pd.read_csv(cache_path)
    assert set(new_cache["appid"]) == {1, 2}


def test_enrich_data_pipeline(monkeypatch):
    # Stub out update_current_players to avoid I/O
    monkeypatch.setattr(
        enrich, 
        "update_current_players", 
        lambda df: df.assign(current_players=5)
    )

    # Raw DataFrame with all needed columns
    df = pd.DataFrame({
        "release_date": [pd.to_datetime("2022-01-01")],
        "peak_ccu": [0],
        "price": ["10"],
        "estimated_owners": [10],
        "positive": [7],
        "negative": [3],
    })

    out = enrich.enrich_data(df.copy())

    # It should have applied all enrich_* steps in order:
    assert "release_year" in out.columns
    assert "estimated_revenue" in out.columns
    assert out.loc[0, "current_players"] == 5
    assert "positive_ratio" in out.columns
