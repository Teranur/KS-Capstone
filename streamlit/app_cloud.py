from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import sqlalchemy
import streamlit as st


# Environment variables are loaded from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
dotenv_path = PROJECT_ROOT / ".env.dev"
if not dotenv_path.exists():
    raise FileNotFoundError(f".env.dev not found at {dotenv_path}")
load_dotenv(dotenv_path, override=True)

st.set_page_config(
    page_title="🎮 Steam Games Dashboard",
    layout="wide",
)

# Title
st.markdown(
    "<h1 style='text-align: center;'>🎮 Steam Games Dashboard</h1>",
    unsafe_allow_html=True,
)


# caches the engine so the connection is reused
@st.cache_resource
def get_engine():
    cfg = st.secrets  # load all secrets
    user = cfg["DB_USER"]
    pwd = cfg.get("DB_PASSWORD", "")
    host = cfg["DB_HOST"]
    port = cfg.get("DB_PORT", "5432")
    dbname = cfg["DB_NAME"]
    schema = cfg.get("DB_SCHEMA", "c12de")

    url = (
        f"postgresql+psycopg2://{user}:{pwd}"
        f"@{host}:{port}/{dbname}"
    )
    engine = sqlalchemy.create_engine(
        url, connect_args={"options": f"-csearch_path={schema}"}
    )
    return engine


# caches the data for 10 minutes
@st.cache_data(ttl=600)
def load_data():
    return pd.read_sql("SELECT * FROM kr_so_capstone", get_engine())


# loads the data from pagila
df = load_data()


# Filtering options
st.sidebar.header("Filters")
genres = sorted({
    g.strip()
    for cell in df["genres"].dropna()
    for g in cell.split(",")
})
categories = sorted({
    c.strip()
    for cell in df["categories"].dropna()
    for c in cell.split(",")
})
years = sorted(df["release_year"].dropna().unique())
price_tiers = sorted(df["price_tier"].dropna().unique())

sel_genres = st.sidebar.multiselect("Genres", genres, default=[])
sel_categories = st.sidebar.multiselect("Categories", categories, default=[])
sel_years = st.sidebar.multiselect("Release Year", years, default=[])
sel_tiers = st.sidebar.multiselect("Price Tier", price_tiers, default=[])
# filtering logic
mask = pd.Series(True, index=df.index)
if sel_genres:
    mask &= (
        df["genres"]
        .fillna("")
        .apply(lambda cell: any(g in cell for g in sel_genres))
    )
if sel_categories:
    mask &= (
        df["categories"]
        .fillna("")
        .apply(lambda cell: any(c in cell for c in sel_categories))
    )
if sel_years:
    mask &= df["release_year"].isin(sel_years)
if sel_tiers:
    mask &= df["price_tier"].isin(sel_tiers)

filtered = df[mask]

# Games per year
st.subheader("Games Released per Year")
release_counts = filtered.groupby("release_year").size().sort_index()
st.bar_chart(release_counts)

# games per current players
st.subheader("Top Games by Current Players")
top_n = st.slider("Display Top Games", min_value=5, max_value=50, value=10)
top_df = filtered.nlargest(top_n, "current_players").reset_index(drop=True)

if "selected_game" not in st.session_state:
    st.session_state.selected_game = None

# Gallery of top games
if st.session_state.selected_game is None:
    cols = st.columns(5)
    for idx, row in top_df.iterrows():
        col = cols[idx % 5]
        with col:
            # Display cover and caption
            st.image(
                row["header_image"],
                caption=row["name"],
                use_container_width=True
            )
            # Center the Details button via three sub-columns
            left, center, right = col.columns([1, 2, 1])
            with center:
                if st.button("Details", key=f"details_{idx}"):
                    st.session_state.selected_game = row["name"]
    st.stop()
# Details view
game = df[df["name"] == st.session_state.selected_game].iloc[0]

# game title
st.markdown(
    f"<h2 style='text-align: center;'>🕹️ {game['name']}</h2>",
    unsafe_allow_html=True
)


# Back button
def clear_selection():
    st.session_state.selected_game = None


st.button("← Back to gallery", on_click=clear_selection)

# game details
c1, c2 = st.columns([1, 2])
with c1:
    if pd.notna(game["header_image"]):
        st.image(game["header_image"], use_container_width=True)

with c2:
    # Split into two sub‐columns for readability
    m1, m2 = st.columns(2)

    with m1:
        st.write("**Price:**", f"${game['price']:.2f}")
        st.write("**Price tier:**", game["price_tier"])
        st.write("**Current players:**", f"{game['current_players']:,}")
        est_rev_k = game["estimated_revenue"] / 1000
        st.write("**Est. revenue:**", f"${est_rev_k:.1f} k")
        st.write("**Metacritic score:**", game["metacritic_score"])
        st.write("**Positive ratio:**", f"{game['positive_ratio']:.1f}%")

    with m2:
        st.write("**Release date:**", game["release_date"])
        st.write("**Developers:**", game["developers"])
        st.write("**DLC count:**", int(game["dlc_count"]))
        platforms = ", ".join(
            p for p in ("Windows", "Mac", "Linux") if game[p.lower()]
        )
        st.write("**Platforms:**", platforms)
        st.write("**Categories:**", game["categories"])
        st.write("**Genres:**", game["genres"])

# Full description below the metrics
st.markdown("### About the game")
st.write(game["about_the_game"])