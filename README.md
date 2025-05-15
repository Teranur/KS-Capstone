## KS-Capstone: Digital Futures Capstone Project

### Overview

This repository contains an analysis of Steam games released through March 2025. Leveraging a dataset from Kaggle, it examines market trends, peak concurrent player counts, engagement patterns, and revenue projections. Results are accessible via an interactive Streamlit dashboard, enabling dynamic filtering by release year, genre, and other attributes.

### Objectives

* **Trend Analysis:** Track the evolution of game genres, categories, and key features over time.
* **Performance Ranking:** Identify top-performing titles based on peak concurrent players.
* **Engagement Insights:** Evaluate player behavior and retention patterns.
* **Revenue Estimation:** Project revenue using player metrics and pricing models.
* **Interactive Visualization:** Deliver a user-friendly Streamlit dashboard for exploratory analysis.

### Dataset

* **Source:** [Kaggle: Steam Games Dataset](https://www.kaggle.com/datasets/artermiloff/steam-games-dataset)
* **Contents:** Game titles, release dates, categories, genres, player counts, Metacritic scores, and additional metadata.

### ETL Process

1. **Extract:** Download the raw dataset from Kaggle.
2. **Transform:** Clean and normalize data using Python and Pandas.
3. **Load:** Export the processed data to CSV for integration with the dashboard.

### Tools & Technologies

* **Language:** Python
* **Libraries:** Pandas (data manipulation), Streamlit (dashboard)
* **Environment:** venv for dependency isolation

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Teranur/KS-Capstone.git
   cd KS-Capstone
   ```
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .\.venv\\Scripts\\activate  # Windows
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirement-setup.txt
   pip install -e .
   ```

### Usage

#### ETL Pipeline

Run the pipeline in development mode:

```bash
run_etl dev
```

Ensure the required environment variables are set before execution.

#### Streamlit Dashboard

Launch the dashboard locally:

```bash
streamlit run streamlit/app.py
```

To deploy to Streamlit Community Cloud, use:

```bash
streamlit run app_cloud.py
```

Configure secrets in the Streamlit UI for necessary environment variables.
