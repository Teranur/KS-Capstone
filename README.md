Digital Futures Capstone Project
This repository implements an end-to-end ETL pipeline and interactive Streamlit dashboard for Steam games data through March 2025. We extract from Kaggle, clean & enrich the data, load it into PostgreSQL, and surface insights via Streamlit.

Overview
Scope: Steam titles released up to March 2025, with metadata on genres, categories, pricing, player counts, and user sentiment.

End result: A web-hosted dashboard showing your top games by current players, review ratios, revenue estimates, and more—filterable by year, price tier, genre, etc.

Objectives
Genre & category evolution

Top titles by concurrent players

Player engagement & retention trends

Revenue projection models

Streamlit dashboard for interactive exploration

Data Source
Kaggle: artermiloff/steam-games-dataset

Key fields: appid, name, release_date, price, genres, categories, positive/negative reviews, estimated_owners, current_players, etc.

ETL Process
Extract

Download CSV via Kaggle API

Transform

Drop irrelevant columns, de-duplicate

Parse dates, normalize list fields (genres, categories)

Compute mid-point of estimated_owners ranges

Tier prices, calculate estimated_revenue

Fetch & cache live current_players via Steam API

Derive positive_ratio

Load

Create schema & table in PostgreSQL

Truncate and bulk-COPY enriched CSV

Tools & Technologies
Python (3.8+)

Pandas & NumPy

SQLAlchemy + psycopg2 (PostgreSQL)

Streamlit (dashboard)

pytest, flake8, sqlfluff (testing & linting)

Features
Default Top 10 games by current players

Filters: Release year, Price tier, Genres, Categories

“Details” view for individual game metrics & header image

Cached API calls (10 min) for performance

Deployable on Streamlit Community or self-hosted

Getting Started
Clone the repo

bash
Copy
Edit
git clone https://github.com/Teranur/KS-Capstone.git
cd KS-Capstone
Install in editable mode

bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e .
Create your environment files

At the project root, copy and edit:

bash
Copy
Edit
cp .env.dev.example .env.dev
Populate .env.dev with:

# Steam API
STEAM_API_KEY=your_steam_api_key

# Postgres (local or remote)
DB_USER=
DB_PASSWORD=…
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_SCHEMA=
TABLE=kr_so_capstone
Run the full ETL

bash
Copy
Edit
# Loads .env.dev, then Extract→Transform→Load
run_etl dev
Start the dashboard

bash
Copy
Edit
streamlit run streamlit/app.py
Run tests & linters

bash
Copy
Edit
# All unit, integration, component tests + flake8 + sqlfluff
pytest -q
flake8
sqlfluff lint etl/sql