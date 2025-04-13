# 🧩 League of Legends Data Pipeline

> **Status**: In Development  
> **Purpose**: Automated, configurable data pipeline for fetching, filtering, and storing *League of Legends* match data using Riot's official API.

---

## 🔍 Overview

This repository contains a modular, rate-limited, and well-logged data pipeline built around the [Riot Games API](https://developer.riotgames.com/). It automates the process of:

- Retrieving ranked match data across tiers and roles
- Filtering relevant events and timelines
- Storing structured results in a local SQLite database
- Preparing clean datasets for statistical analysis and machine learning

---

## 🏗️ Folder Structure

lol-data-pipeline/
|
├── riot_api.py                # Riot API wrapper class
├── pipeline_workflow.py       # Orchestrates the entire pipeline
|
├── processing/
|   └── response_filters.py    # Functions to clean/filter JSON data (NOT YET FUNCTIONAL)
|
├── riot_key_folder/
|   └── riot_api_key.py        # Riot API key loading (excluded from Git)
|
├── logs/
|   └── riot_data.log          # Rotating logs for error tracking and debugging
|
├── database/
|   └── riot_data_database.db  # Local SQLite database for structured match storage
|
├── configs/
|   └── logging_config.yaml    # Logging configuration for customization
|
└── README.md


---

## ⚙️ Features

### 🔗 Riot API Interface (`riot_api.py`)
- Interacts with Riot’s Match-V5, Summoner-V4, and Spectator-V4 endpoints
- Fetches player PUUIDs, match histories, and timelines
- Implements robust error handling and rate limit compliance

### 🧠 Pipeline Controller (`pipeline_workflow.py`)
- End-to-end orchestration of:
  - Player and match data retrieval
  - Timeline extraction
  - Filter application and database storage
- Enables batch collection and control over sample size and rank tier

### 🧼 JSON Filtering Module (`processing/response_filters.py`)
- Extracts:
  - Key game events (kills, dragons, barons, towers)
  - Player stats and item builds
  - Timeline information for positional or time-based analyses

### 🧱 Database Integration (`riot_data_database.db`)
- Lightweight SQLite database setup
- Stores structured data across:
  - Match metadata
  - Participant performance
  - Event sequences and timelines

### 🪵 Logging System (`logs/riot_data.log`)
- Tracks request success/failure and error messages
- Useful for debugging long pipeline runs
- Controlled via `configs/logging_config.yaml`

---

## 🧪 How to Run

```bash
# Clone repo
git clone https://github.com/yourusername/lol-data-pipeline.git

# Set up environment
pip install -r requirements.txt

# Add your Riot API Key
echo "RIOT_API_KEY=your_api_key_here" > riot_key_folder/riot_api_key.py

# Run the pipeline
python pipeline_workflow.py
