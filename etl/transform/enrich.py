import os
import time
import pandas as pd
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
SESSION = requests.Session()
CACHE_PATH = Path("data") / "steam_players_cache.csv"


def fetch_current_players(appid: int) -> int:
    #  make a call to the Steam API to get the current players
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    params = {"key": STEAM_API_KEY, "appid": appid}
    try:
        resp = SESSION.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json().get("response", {}).get("player_count", 0)
    except requests.RequestException:
        return 0


def load_player_cache() -> pd.DataFrame:
    #  since we have over 70k games, we need to cache the current players
    #  to avoid hitting the API limit
    if CACHE_PATH.exists():
        return pd.read_csv(CACHE_PATH, dtype={"appid": int, "current_players": int})
    return pd.DataFrame(columns=["appid", "current_players"])


def save_player_cache(df_cache: pd.DataFrame):
    #  save the cache to a CSV file
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_cache.to_csv(CACHE_PATH, index=False)


def update_current_players(df: pd.DataFrame) -> pd.DataFrame:
    #  check if the current players column is empty
    cache = load_player_cache()
    #  merge the cache with the dataframe
    df = df.merge(cache, on="appid", how="left", suffixes=("", "_cached"))
    df["current_players"] = df["current_players"].fillna(0).astype(int)
    df["current_players"] = df.apply(
        lambda r: r["current_players_cached"]
        if pd.notna(r["current_players_cached"]) else r["current_players"],
        axis=1
    )
    df.drop(columns=["current_players_cached"], inplace=True)
    #  filter the dataframe to get the appids with current players = 0
    mask = df["current_players"] == 0
    appids = df.loc[mask, "appid"].astype(int).unique()
    new_entries = []
    #  as we are making a lot of requests,
    # we need to do it in parallel to reduce the time it takes
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_current_players, aid): aid for aid in appids}
        for future in as_completed(futures):
            aid = futures[future]
            count = future.result()
            new_entries.append({"appid": aid, "current_players": count})

    if new_entries:
        #  compare the new entries with the cache
        new_cache = pd.DataFrame(new_entries)
        cache = pd.concat([cache, new_cache],
                        ignore_index=True).drop_duplicates("appid", keep="last")
        save_player_cache(cache)
        #  merge the new cache with the dataframe
        df = df.merge(new_cache, on="appid", how="left", suffixes=("", "_new"))
        df.loc[df["current_players"] == 0,
               "current_players"] = df["current_players_new"]
        df.drop(columns=["current_players_new"], inplace=True)

    return df


def enrich_dates(df: pd.DataFrame) -> pd.DataFrame:
    #  rename the peak_ccu column to current_players as the data is miss labeled
    df = df.rename(columns={"peak_ccu": "current_players"})
    #  get the year and month for filtering purposes later
    df["release_year"] = df["release_date"].dt.year
    df["release_month"] = df["release_date"].dt.month
    return df


def enrich_price(df: pd.DataFrame) -> pd.DataFrame:
    #  convert the price to numeric and calculate the estimated revenue
    df["price_numeric"] = df["price"].apply(
        lambda x: 0.0 if x in (0, "Free") else float(x)
        )
    #  get the estimated revenue by multiplying the estimated owners by the price
    df["estimated_revenue"] = (
        df["estimated_owners"] * df["price_numeric"] * 0.7).round(1)
    #  categorize the price into tiers
    
    def tier(p):
        if p == 0 or p == "Free":
            return "Free"
        if p <= 25:
            return "Indie"
        if p <= 40:
            return "Standard"
        return "Premium"
    #  apply the tier function to the price_numeric column
    df["price_tier"] = df["price_numeric"].apply(tier)
    return df


def enrich_metrics(df: pd.DataFrame) -> pd.DataFrame:
    #  calculate the positive and negative ratios
    df["positive_ratio"] = (df["positive"] / (df["positive"] + df["negative"]) * 100).round(1)
    df["recommendation_rate"] = (df["recommendations"] / df["estimated_owners"] * 100).round(1)
    return df


def enrich_counts(df: pd.DataFrame) -> pd.DataFrame:
    # get the counts of the genres and categories
    df["genre_count"] = df["genres"].fillna("").str.split(",").apply(len)
    df["category_count"] = df["categories"].fillna("").str.split(",").apply(len)
    return df


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    #  execute the enrichment functions in order
    df = enrich_dates(df)
    df = enrich_price(df)
    df = update_current_players(df)
    df = enrich_metrics(df)
    df = enrich_counts(df)
    return df


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    CLEAN_PATH = DATA_DIR / "steam_games_clean.csv"
    ENRICH_PATH = DATA_DIR / "steam_games_enriched.csv"

    df = pd.read_csv(CLEAN_PATH, parse_dates=["release_date"])
    start = time.perf_counter()
    df_enriched = enrich_data(df)
    elapsed = time.perf_counter() - start
    df_enriched.to_csv(ENRICH_PATH, index=False)
    print(f"Enrichment completed in {elapsed:.2f} seconds.")
    print(df_enriched.head())
    zero_count = (df_enriched["current_players"] == 0).sum()
    total = len(df_enriched)
    print(f"Entries with current_players == 0: {zero_count} / {total} ({zero_count/total:.1%})")
