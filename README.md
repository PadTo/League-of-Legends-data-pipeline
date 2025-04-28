# 🧩 League of Legends Data Pipeline

- **Status**: Completed
- **Purpose**: Automated, configurable data pipeline for fetching, filtering, and storing _League of Legends_ match data using Riot's official API.
- **Additional Advanced Features to be Added in the Future**:
  - A class that will include functions to fetch data from the tables based on the desired parameters

---

## 🔍 Overview

This repository contains a modular, rate-limited, and well-logged data pipeline built around the [Riot Games API](https://developer.riotgames.com/). It automates the process of:

- Retrieving ranked match data across tiers and roles
- Filtering relevant events and timelines
- Storing structured results in a local SQLite database
- Preparing clean datasets for statistical analysis and machine learning

---

## 🏗️ Folder Structure

<pre>

League-of-Legends-data-pipeline/
├── data/
├── log_config/
│   ├── log_config.json
├── logs/
├── notebooks/
│   ├── playground.ipynb
├── src/
│   ├── __pycache__/
│   ├── data_collection/
│   │   ├── __ini__.py
│   │   ├── riot_api.py
│   ├── pipeline/
│   │   ├── __init__py
│   │   ├── pipeline_workflow.py
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── LoLDatabaseQuery.py
│   ├── riot_key_folder/
│   │   ├── __init__.py
│   │   ├── config_template.json
│   │   ├── riot_api_key.py
│   ├── RiotAPI_Processing_Functions.egg-info/
│   ├── __init__.py
├── .gitignore
├── photos/
│   ├── API_Call_Workflow.png
│   ├── Database_Tables_Relationships
├── documentation.txt
├── pipeline_configuration
├── main.py
├── README.md
├── setup.py
</pre>

---

## 🗃️ Database Schema

![Database Tables Relationships](photos/Database_Tables_Relationships.png)

# 🔁 API Call Workflow

## Overview

This workflow describes fetching and storing League of Legends match data through Riot Games' API.

![API Call Workflow](photos/API_Call_Workflow.png)

## Workflow Steps

### 1. Input Queue, Tier, Division

- **Input**: Competitive tier (e.g., Challenger, Iron), queue (e.g., ranked, normal), and division (e.g., I, II)
- **API Call**: `/lol/league/v4/entries/{queue}/{tier}/{division}`
- **Action**:
  - Retrieve summoner entries for each tier and division (ranked)
  - Store data in SQL database

### 2. Get Match IDs from puuIDs

- **Fetch**: puuID from the database
- **API Call**: `/lol/match/v5/matches/by-puuid/{puuid}/ids`
- **Action**:
  - Get the list of recent match IDs for each player
  - Store data in an SQL database

### 3. Get Match Data

- **Fetch**: matchID from the database
- **API Call**: `/lol/match/v5/matches/{matchId}`
- **Extract**:
  - Participant-level data
  - Team-level data

### 4. Get Match Timeline

- **Fetch**: matchID from the database
- **API Call**: `/lol/match/v5/matches/{matchId}/timeline`
- **Extract**:
  - Events data
  - Frame-by-frame gameplay data

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

### 🧼 Filtering Module (IN PROGRESS)

- TBD

### 🧱 Database Integration (`riot_data_database.db`)

- Lightweight SQLite database setup
- Stores structured data across:
  - Match metadata
  - Participant performance
  - Event sequences and timelines

### 🪵 Logging System (`logs/riot_data.log`)

- Tracks request success/failure and error messages
- Useful for debugging long pipeline runs
- Controlled via `configs/log_config.json`

---

## 🧪 How to Run

### Installation

To install the RiotAPI Processing Functions locally, follow these steps:

Clone the repository:

<pre>
  git clone https://github.com/PadTo/League-of-Legends-data-pipeline.git
  cd League-of-Legends-data-pipeline
</pre>

Run the following command to install the package locally:

<pre>
  pip install .
</pre>

Make sure you're in the root directory of the project (where setup.py is located) before running the install command.

### ⚙️ Configure the Pipeline

Edit the pipeline_configuration.json file located in the project root. This file contains all runtime settings required by the pipeline:

EXAMPLE:

<pre>
{
  "database_save_location": "YOUR/DESIRED/DATA/PATH",
  "logging_configuration_filepath": "YOUR/DESIRED/LOG_CONFIG_PATH/log_config.json",
  "stages_to_process": [0, 1, 0, 0], 
  "rate_limit": -1,
  "region": -1,
  "page_limit": -1,
  "event_types_to_consider": -1,
  "batch_insert_limit": -1,
  "match_ids_per_tier": 10000,
  "matches_per_tier": 10000
}
</pre>

⚠️ CONFIGURATION EXPLANATION:

"database_save_location":

- Path where processed data will be saved (e.g., a .db or .sqlite file).
- Example: "./data/match_data.db"
- Make sure this path exists or the program has permissions to create it.

"logging_configuration_filepath":

- Path to the logging config file (usually a JSON file).
- Controls logging behavior: what to log, where to log it, log level, etc.
- Example: "./config/log_config.json"

"stages_to_process":

- A list of 4 binary values [1, 1, 1, 1] to toggle pipeline stages.
  - 1 = run the stage
  - 0 = skip the stage
- Example: [1, 1, 0, 0] runs only stages 1 and 2.
- Dependency rules:
  - Stage 2 depends on stage 1
  - Stage 3 depends on stage 2
  - Stage 4 depends on stage 3

"rate_time_limit":

- API rate limit in format [calls, seconds].
- Example: [100, 120] = 100 requests allowed per 120 seconds.
- Prevents hitting Riot API limits and being throttled or blocked.

"region":

- Riot API region URL to query from.
- Only European regions are allowed (e.g., "https://eun1.api.riotgames.com").
- Using unsupported regions will break the pipeline.

"page_limit":

- Controls how many pages of match data are fetched per tier/division in stage 1.
- Set to -1 to disable the limit (fetch all available pages).
- Example: 5 = fetch up to 5 pages per bracket.

"eventTypesToConsider":

- Filters which event types to extract from match timelines.
- Example: ["CHAMPION_KILL", "BUILDING_KILL", "ELITE_MONSTER_KILL"]
- Customize to include only relevant game events.

"batch_insert_limit":

- Maximum number of entries to insert into the database at once.
- Helps avoid memory overload and improves performance.
- Default: 1000 (specific behaviour varies based on processing stage, but a general parameter to control the flow of data)
- Batching prevents issues with RAM usage and large single-query loads.

"match_ids_per_tier":

- Number of match IDs to randomly select per tier before processing.
- Can be an integer (absolute number) or float (proportion of total).
- Example: 10000 = select 10,000 match IDs per tier. 0.25 = select 25% of all match IDs per tier.
- If the value is set to `-1`, then all of the available data is processed.

"matches_per_tier":

- Number of full matches to load and process per tier.
- Controls how much detailed match data is fetched via the Riot API.
- Example: 10000 = parse 10,000 full matches per tier. 0.25 = select 25% of all match IDs per tier.
- If the value is set to `-1`, then all of the available data is processed.

### Run the Main Script

python main.py

When you run the file, you will be prompted to input your Riot API key. You can choose to replace it or skip it.

<pre>
  Do you want to replace the API key (Y for YES | N for NO)?
  If you type Y, you'll be prompted to enter your Riot API key:
</pre>

Once the key is entered, the pipeline will start and begin processing data.

NOTE:

- The collection process takes a long time (Hours) due to rate limiting (rate limits can be adjusted based on your needs and account constraints related to rates)
- The data WILL NOT be uploaded due to the database having millions of entries
- If the pipeline's API calls have request code 400 even though the API key is valid, re-generating the key might fix the problem
