import os
import time
import pandas as pd
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
SESSION = requests.Session()
CACHE_PATH = Path("data") / "steam_players_cache.csv"


# makes a call to the Steam API to get the current players for a given appid
def fetch_current_players(appid: int) -> int:
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    params = {"key": STEAM_API_KEY, "appid": appid}
    try:
        resp = SESSION.get(url, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json().get("response", {}).get("player_count", 0)
    except requests.RequestException:
        return 0

# we making a lot of ccalls to the Steam API
#  so we need to cache the results to avoid hitting the rate limit
def load_player_cache() -> pd.DataFrame:
    if CACHE_PATH.exists():
        return pd.read_csv(CACHE_PATH, dtype={"appid": int, "current_players": int})
    return pd.DataFrame(columns=["appid", "current_players"])


# naturally we got to have the cache saved
def save_player_cache(df_cache: pd.DataFrame):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_cache.to_csv(CACHE_PATH, index=False)

# update the current players column in the dataframe
#  by merging with the cache and fetching new data
def update_current_players(df: pd.DataFrame) -> pd.DataFrame:
    cache = load_player_cache()
    df = df.merge(cache, on="appid", how="left", suffixes=("", "_cached"))
    df["current_players"] = df["current_players"].fillna(0).astype(int)
    df["current_players"] = df.apply(
        lambda r: r["current_players_cached"]
        if pd.notna(r["current_players_cached"]) else r["current_players"],
        axis=1
    )
    df.drop(columns=["current_players_cached"], inplace=True)

    mask = df["current_players"] == 0
    appids = df.loc[mask, "appid"].astype(int).unique()
    new_entries = []
    # we have to use threading to avoid hitting the rate limit
    #  and to speed up the process it still takes 15min
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_current_players, aid): aid for aid in appids}
        for future in as_completed(futures):
            aid = futures[future]
            new_entries.append({"appid": aid, "current_players": future.result()})
    # updates the cache with new entries
    #  and merges with the dataframe
    # also makes sure they are integers, had to come back to this
    if new_entries:
        new_cache = pd.DataFrame(new_entries)
        cache = pd.concat([cache, new_cache], ignore_index=True) \
            .drop_duplicates("appid", keep="last")
        save_player_cache(cache)
        df = df.merge(new_cache, on="appid", how="left", suffixes=("", "_new"))
        df.loc[
            df["current_players"] == 0, "current_players"
        ] = df["current_players_new"]
        df.drop(columns=["current_players_new"], inplace=True)
    df["current_players"] = (
        pd.to_numeric(df["current_players"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return df


# rename the peak_ccu column to current_players
#  and add a release_year column for filtering and grouping
def enrich_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"peak_ccu": "current_players"})
    df["release_year"] = df["release_date"].dt.year
    return df


# make a numeric price column with estimated revenue and price tiers
# had plans for the price but they got abandoned
def enrich_price(df: pd.DataFrame) -> pd.DataFrame:
    # Temporarily convert price to numeric for computations
    df["price_numeric"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Estimated revenue
    # steam takes a 30% cut from the sales
    df["estimated_revenue"] = (
        df["estimated_owners"] * df["price_numeric"] * 0.7
    ).round(1)

    # Price tiers, im sure you heard of these clasifications
    def tier(p):
        if p == 0:
            return "Free"
        if p <= 25:
            return "Indie"
        if p <= 40:
            return "Standard"
        return "Premium"

#  and look at that we got a new column
    df["price_tier"] = df["price_numeric"].apply(tier)

    # we kind of dont need it anymore so away it goes
    # trust me i did need it before
    # will get cleaned up later
    df.drop(columns=["price_numeric"], inplace=True)
    return df


# calculate the positive ratio from the positive and negative reviews
def enrich_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df["positive_ratio"] = (
        df["positive"] / (df["positive"] + df["negative"]) * 100
    ).round(1)
    return df


# execute order 66 "cleaning"
def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    df = enrich_dates(df)
    df = enrich_price(df)
    df = update_current_players(df)
    df = enrich_metrics(df)
    return df


# timer + file paths, remember children when you struggling brute force it
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    CLEAN_PATH = BASE_DIR / "data" / "steam_games_clean.csv"
    ENRICH_PATH = BASE_DIR / "data" / "steam_games_enriched.csv"

    df = pd.read_csv(CLEAN_PATH, parse_dates=["release_date"])
    start = time.perf_counter()
    df_enriched = enrich_data(df)
    df_enriched.to_csv(ENRICH_PATH, index=False)
    print(f"Enrichment completed in {time.perf_counter() - start:.2f} seconds.")
