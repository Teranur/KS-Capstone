# KS-Capstone
Digital Futures Capstone Project
Overview
This project presents an in-depth analysis of Steam games released up to the year 2025. Using a dataset sourced from Kaggle, it explores key market trends, peak concurrent player counts, player engagement patterns, and projected revenue. The results are presented through an interactive Streamlit dashboard that allows users to filter and explore insights by release year, genre, and other attributes.

Objectives
Analyze the evolution of game genres, categories, and key features over time.

Identify top-performing titles based on peak concurrent player counts.

Evaluate player engagement trends and retention patterns.

Estimate revenue projections using player metrics and pricing models.

Provide an intuitive, interactive Streamlit dashboard for data exploration.

Dataset
Source: Kaggle

The dataset includes game titles, release dates, categories, genres, peak player counts, and other relevant metadata.
https://www.kaggle.com/datasets/joebeachcapital/top-1000-steam-games/data

ETL Process
Extract: Load the dataset from Kaggle.

Transform: Clean and preprocess data using Python (pandas, NumPy) to ensure consistency and usability.

Load: Save the transformed data to CSV for dashboard integration.

Tools & Technologies
Python – Data manipulation and processing

Pandas – Data cleaning and transformation

Streamlit – Interactive dashboard development

Matplotlib / Plotly – Visualizations

Features
Dynamic filtering by release year, genre, and category

Visual trends of peak concurrent player counts

Summary metrics (e.g., top games, average players, estimated revenue)

Clean, responsive UI for data interaction

Getting Started
Clone the repository

Install dependencies

Run the Streamlit app:

    streamlit run app.py
